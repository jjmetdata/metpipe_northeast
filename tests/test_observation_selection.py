import sys
from pathlib import Path
import unittest
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analysis'))
from observation_selection import decode_metar, resolve_number, resolve_wind

T = pd.Timestamp('2024-12-26T14:51Z')
FLAGS = {'s':'343','q':'5'}


class SelectionTests(unittest.TestCase):
    def test_rounding_agreement_primary_unchanged(self):
        self.assertIsNone(resolve_number('station_pressure_hpa',1042.5,1042.669,T,T,FLAGS))

    def test_exact_time_and_station_metar(self):
        text='MET083METAR KPWM 261451Z 35004KT 10SM CLR M03/M08 A3051 RMK AO2 T10331078'
        result=decode_metar(text,'PWM',T)
        self.assertEqual(result['temperature_c'],-3.3)
        self.assertEqual(result['dewpoint_c'],-7.8)
        self.assertNotIn('station_pressure_hpa',result)
        self.assertNotIn('relative_humidity',result)
        self.assertFalse(decode_metar(text,'PVC',T))
        self.assertFalse(decode_metar(text,'PWM',T+pd.Timedelta(hours=1)))
        self.assertFalse(decode_metar('FAKEMETAR KPWM 261451Z RMK T10331078','PWM',T))

    def test_portland_conflict_selects_lcd_support(self):
        metar=decode_metar('METAR KPWM 261451Z 35004KT RMK T10331078','PWM',T)
        d=resolve_number('temperature_c',-1.7,-3.3333333,T,T,FLAGS,metar=metar)
        self.assertEqual(d['source'],'LCDv1')
        self.assertAlmostEqual(d['value'],-3.3333333)
        self.assertIn('embedded_METAR',d['reason'])

    def test_unresolved_blanks_only_element(self):
        d=resolve_number('relative_humidity',82.,89.,T,T,FLAGS)
        self.assertIsNone(d['value'])
        self.assertEqual(d['reason'],'conflict_unresolved')
        self.assertEqual(d['ghcnh_value'],82.)
        self.assertEqual(d['lcd_value'],89.)
        self.assertIsNone(resolve_number('wind_speed_ms',2.,2.1,T,T,FLAGS))

    def test_fallback_blocks_bad_primary_qc(self):
        d=resolve_number('temperature_c',None,10.,T,T,{'s':'343','q':'3'})
        self.assertIsNone(d['value'])
        self.assertIn('blocked',d['reason'])

    def test_missing_primary_fallback_and_suspect_lcd(self):
        d=resolve_number('temperature_c',None,10.,None,T,{})
        self.assertEqual(d['source'],'LCDv1')
        self.assertEqual(d['value'],10.)
        d=resolve_number('temperature_c',None,10.,None,T,{},lcd_suspect=True)
        self.assertIsNone(d['value'])

    def test_fallback_report_times_not_silently_mixed(self):
        d=resolve_number('temperature_c',None,10.,T+pd.Timedelta(minutes=3),T,{})
        self.assertIsNone(d['value'])
        self.assertIn('report_time',d['reason'])

    def test_precip_trace_and_reported_amount(self):
        t=pd.Timestamp('2024-12-11T19:51Z')
        m=decode_metar('METAR KPVD 111951Z 18024G37KT RMK P0036','PVD',t)
        d=resolve_number('precipitation_reported_mm',3.8,9.144,t,t,FLAGS,metar=m,gh_trace=False,lcd_trace=False)
        self.assertEqual(d['source'],'LCDv1')
        self.assertEqual(d['value'],9.144)
        m=decode_metar('METAR KPVD 111951Z 18024KT RMK P0000','PVD',t)
        self.assertTrue(m['precipitation_trace'])

    def test_wind_wraparound_and_calm_not_north(self):
        self.assertIsNone(resolve_wind('numeric',360.,'numeric',0.,T,T,FLAGS,{}))
        d=resolve_wind('missing',None,'calm',None,None,T,{}, {})
        self.assertEqual(d['state'],'calm')
        self.assertIsNone(d['value'])

    def test_conflict_without_direct_pressure_truth_stays_null(self):
        d=resolve_number('station_pressure_hpa',1000.,1002.,T,T,FLAGS,metar={'altimeter_hpa':1000.})
        self.assertIsNone(d['value'])

    def test_primary_override_keeps_trace_flag(self):
        d=resolve_number('precipitation_reported_mm',0.,1.,T,T,FLAGS,lcd_suspect=True,gh_trace=True,lcd_trace=False)
        self.assertEqual(d['source'],'GHCNh')
        self.assertTrue(d['trace'])

    def test_malformed_or_coarse_temperature_not_adjudicated(self):
        m=decode_metar('METAR KPWM 261451Z 35004KT M03/M08 A3051','PWM',T)
        self.assertNotIn('temperature_c',m)
        d=resolve_number('temperature_c',-1.7,-3.333333,T,T,FLAGS,metar=m)
        self.assertIsNone(d['value'])


if __name__ == '__main__':
    unittest.main()
