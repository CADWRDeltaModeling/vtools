import sys,os,unittest,shutil,random,pdb
# diff function import
from group import *
from vtools.data.vtime import *
from vtools.data.timeseries import *
from numpy import array,isnan


class TestGroup(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):
        super(TestGroup,self).__init__(methodName)
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000

    def test_group_by_nan(self):

        data = [1,2,3]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0],[0,2])

        data = [1,2,3,nan,nan]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0],[0,4])

        data = [nan,nan,1,2,3]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0],[0,4])

        data = [nan,nan,nan,1,2,3]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0],[3,5])

        data = [1,2,3,nan,nan,nan]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0],[0,2])

        data = [1,2,3,nan,nan,nan,4,5,6,nan,nan,7,8]
        compress_size =3
        groups= group_by_nan(data,compress_size)
        self.assertEqual(len(groups),2)
        self.assertEqual(groups[0],[0,2])
        self.assertEqual(groups[1],[6,12])

    def test_ts_group(self):

        ts_data = [1,2,3,nan,nan,nan,4,5,6,nan,nan,7,8]
        compress_size =3
        ts_start = parse_time("01/02/2000 23:00")
        interval = parse_interval("1day")
        props={"aggregation":"mean", "timestamp":"period_start"}
        ts =rts(ts_data,ts_start,interval,props)
        ts_groups = ts_group(ts,compress_size)
        self.assertEqual(len(ts_groups),2)
        self.assertEqual(len(ts_groups[0]),3)
        self.assertEqual(ts_groups[0].data[0],1.0)
        self.assertEqual(ts_groups[0].data[1],2.0)
        self.assertEqual(ts_groups[0].data[2],3.0)
        self.assertEqual(ts_groups[0].start,ts_start)
        self.assertEqual(ts_groups[0].props, ts.props)
        self.assertEqual(len(ts_groups[1]),7)
        self.assertEqual(ts_groups[1].data[0],4.0)
        self.assertEqual(ts_groups[1].data[1],5.0)
        self.assertTrue(isnan(ts_groups[1].data[3]))
        self.assertEqual(ts_groups[1].data[6],8.0)
        self.assertEqual(ts_groups[1].start,ts_start+parse_interval("6day"))
        self.assertEqual(ts_groups[1].props, ts.props)

if __name__=="__main__":

    unittest.main()
