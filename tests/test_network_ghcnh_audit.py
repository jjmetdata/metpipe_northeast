import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from audit_network_ghcnh import screen_field, select_records, summarize, FIELDS


def row(time='2024-01-01T00:53:00', report='FM15'):
    result = {'DATE': time, 'temperature': 10., 'dew_point_temperature': 5., 'wind_speed': 3.,
              'station_level_pressure': 1000., 'relative_humidity': 70., 'precipitation': None}
    for field in FIELDS:
        result[field+'_Source_Code'] = '343'
        result[field+'_Quality_Code'] = '4'
        result[field+'_Report_Type'] = report
        result[field+'_Measurement_Code'] = ''
    return result


class NetworkAvailabilityTests(unittest.TestCase):
    def test_known_bad_qc_removed_unknown_retained_but_not_certified(self):
        raw = pd.DataFrame([row(),row(),row()])
        raw.loc[0,['temperature_Source_Code','temperature_Quality_Code']] = ['223','5']
        raw.loc[1,['temperature_Source_Code','temperature_Quality_Code']] = ['335','5']
        raw.loc[2,['temperature_Source_Code','temperature_Quality_Code']] = ['999','9']
        values, d = screen_field(raw,'temperature')
        self.assertTrue(pd.isna(values.iloc[0]))
        self.assertEqual(values.iloc[1],10.)
        self.assertEqual(values.iloc[2],10.)
        self.assertTrue(d['full_qc'].iloc[1])
        self.assertTrue(d['unmapped_qc'].iloc[2])

    def test_missing_precip_not_zero_and_accumulations_excluded(self):
        raw = pd.DataFrame([row(),row(),row(),row()])
        raw.loc[1,['precipitation','precipitation_Measurement_Code']] = [0.,'2']
        raw.loc[2,['precipitation','precipitation_Measurement_Code']] = [5.,'4']
        raw.loc[3,['precipitation','precipitation_Report_Type']] = [5.,'FM16']
        values,d=screen_field(raw,'precipitation')
        self.assertTrue(pd.isna(values.iloc[0]))
        self.assertEqual(values.iloc[1],0.)
        self.assertTrue(d['trace'].iloc[1])
        self.assertTrue(values.iloc[2:].isna().all())

    def test_trace_code_two_is_source_specific(self):
        raw=pd.DataFrame([row()])
        raw.loc[0,['precipitation','precipitation_Source_Code','precipitation_Measurement_Code']] = [2.,'382','2']
        value,d=screen_field(raw,'precipitation')
        self.assertEqual(value.iloc[0],2.)
        self.assertFalse(d['trace'].iloc[0])

    def test_coherent_row_no_per_element_best_of_hour(self):
        first=row('2024-01-01T00:50:00')
        second=row('2024-01-01T00:55:00')
        second['temperature']=None
        second['station_level_pressure']=1010.
        chosen,_=select_records(pd.DataFrame([first,second]))
        self.assertEqual(len(chosen),1)
        self.assertEqual(chosen.station_pressure_hpa.iloc[0],1000.)
        self.assertEqual(chosen.actual_time.dt.minute.iloc[0],50)

    def test_specials_and_summaries_do_not_create_routine_hours(self):
        raw=pd.DataFrame([row(report='FM16'),row(report='SOD'),row(report='NSRDB')])
        chosen,_=select_records(raw)
        self.assertEqual(len(chosen),0)

    def test_variable_direction_reported_not_numeric_angle_claim(self):
        raw=pd.DataFrame([row()])
        raw['wind_direction']=np.nan
        raw['wind_direction_Measurement_Code']='V'
        values,d=screen_field(raw,'wind_direction')
        self.assertTrue(values.notna().all())
        self.assertTrue(d['variable'].all())
        raw['wind_direction_Quality_Code']='3'
        self.assertTrue(screen_field(raw,'wind_direction')[0].isna().all())

    def test_calm_placeholder_is_reported_state_not_bearing(self):
        raw=pd.DataFrame([row()])
        raw['wind_direction']=999
        raw['wind_direction_Measurement_Code']='C'
        raw['wind_speed']=0.
        value,d=screen_field(raw,'wind_direction')
        self.assertTrue(value.notna().all())
        self.assertTrue(d['calm'].all())
        self.assertFalse(d['numeric_direction'].any())
        raw['wind_speed']=4.
        self.assertTrue(screen_field(raw,'wind_direction')[0].isna().all())

    def test_missing_file_keeps_expected_hour_denominator(self):
        rows=[]
        for year,status,hours in [(2005,'read',8760),(2006,'confirmed_no_file',0)]:
            data={'station':'BOS','year':year,'expected_hours':8760,'routine_hours':hours,'status':status}
            data.update({column+'_hours':hours for column in FIELDS.values()})
            rows.append(data)
        result=summarize(pd.DataFrame(rows),2005,2006)
        self.assertEqual(result.expected_hours.iloc[0],17520)
        self.assertEqual(result.temperature_c_pct.iloc[0],50.)
        self.assertEqual(result.files_read.iloc[0],1)


if __name__ == '__main__':
    unittest.main()
