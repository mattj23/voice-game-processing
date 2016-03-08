__author__ = 'kingjarrad'

import library.tests
import datetime
import library.temporal

data = library.tests.TestLibrary("data")
blocks = data.break_into_blocks(datetime.timedelta(minutes=4))
for block in blocks["NM003"]:
    first,second = block.split_into_parts(2)
    print "first half"
    first.print_summary()
    print "lag1autocorrelation angle: ", library.temporal.lag_1_autocorrelation(first,"release_angle")
    print "lag1autocorrelation stretch: ", library.temporal.lag_1_autocorrelation(first,"release_stretch")
    results = library.temporal.detrended_fluctuation_analysis(first, "release_angle")
    print "dfa angle: ", results["linear_regression"]["slope"]
    results = library.temporal.detrended_fluctuation_analysis(first, "release_stretch")
    print "dfa stretch: ", results["linear_regression"]["slope"]

    print ""

    print "second half"
    second.print_summary()
    print "lag1autocorrelation angle: ", library.temporal.lag_1_autocorrelation(second,"release_angle")
    print "lag1autocorrelation stretch: ", library.temporal.lag_1_autocorrelation(second,"release_stretch")
    results = library.temporal.detrended_fluctuation_analysis(second, "release_angle")
    print "dfa angle: ", results["linear_regression"]["slope"]
    results = library.temporal.detrended_fluctuation_analysis(second, "release_stretch")
    print "dfa stretch: ", results["linear_regression"]["slope"]