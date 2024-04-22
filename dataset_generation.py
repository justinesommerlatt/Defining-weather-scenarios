import io
import urllib
import pandas as pd
import requests
import csv
import statistics
import datetime


'''---------------------------------------------------------------------------------------------------------------------
------------------------------------------------ DEFINITION OF VARIABLES -----------------------------------------------
---------------------------------------------------------------------------------------------------------------------'''
# definition of the host of the requests
host = "https://dwh.int.slf.ch"

# definition of all the lists for the parameters we'll use
triggerDateTime = []
coordX = []
coordY = []
startZoneElevation = []
startZoneAspect = []
fractureThicknessMean = []
size = []
lat = []
lon = []           
IMIScode = []
IMISlat = []
IMISlon = []
measured_time = []
station_code = []
measure_date = []
measure_time = []
hyear = []
VW_30MIN_MEAN = []
VW_30MIN_MAX = []
DW_30MIN_MEAN = []
TA_30MIN_MEAN = []
RH_30MIN_MEAN = []
RSWR_30MIN_MEAN = []
HS = []
TS0_30MIN_MEAN = []
TS25_30MIN_MEAN = []
TS50_30MIN_MEAN = []
TS100_30MIN_MEAN = []
TSS_30MIN_MEAN = []
DW_30MIN_SD = []
HN_1D = []
HN_12H = []
HN_6H = []
RSWR_30MIN_MEAN_12H_values = []
RSWR_30MIN_MEAN_12H = []
RH_30MIN_MEAN_1H_values = []
RH_30MIN_MEAN_1H = []
VW_30MIN_MEAN_1D_values = []
VW_30MIN_MEAN_1D = []
VW_VALUE = []
datesonly = []
hoursonly = []
minutesonly = []

# define all the columns name for the new dataset generated
col1 = "triggerDateTime"
col2 = "coordX"
col3 = "coordY"
col4 = "startZoneElevation"
col5 = "startZoneAspect"
col6 = "fractureThicknessMean"
col7 = "size"
col8 = "lat"
col9 = "lon"
col10 = "IMIScode"
col11 = "IMISlat"
col12 = "IMISlon"
col13 = "measure_date"
col14 = "hyear"
col15 = "VW_30MIN_MEAN"
col16 = "VW_30MIN_MAX"
col17 = "DW_30MIN_MEAN"
col18 = "TA_30MIN_MEAN"
col19 = "RH_30MIN_MEAN"
col20 = "RSWR_30MIN_MEAN"
col21 = "HS"
col22 = "TS0_30MIN_MEAN"
col23 = "TS25_30MIN_MEAN"
col24 = "TS50_30MIN_MEAN"
col25 = "TS100_30MIN_MEAN"
col26 = "TSS_30MIN_MEAN"
col27 = "DW_30MIN_SD"
col28 = "HN_1D"
col29 = "HN_12H"
col30 = "HN_6H"
col31 = "RSWR_30MIN_MEAN_12H"
col32 = "RH_30MIN_MEAN_1H"
col33 = "VW_30MIN_MEAN_1D"
col34 = "VW_VALUE"

'''---------------------------------------------------------------------------------------------------------------------
------------------------------------------------ DEFINITION OF FUNCTIONS -----------------------------------------------
---------------------------------------------------------------------------------------------------------------------'''
# function to define request
def query(q):
    q = urllib.parse.quote(q)
    url = f"{host}/exp?query={q}"
    r = requests.get(url)
    r.raise_for_status()
    rawData = r.text
    df = pd.read_csv(io.StringIO(rawData), parse_dates=["measure_date"])
    return df

# function that calculates the radiation mean value for the last 12 hours before the event (avalanche)
def radiationMean(date, hours, min, station):
    # will be the list with all different times we need for the measurements
    measurements = []
    # date is in the format : YYYY-MM-DD
    splitted_date = date.split("-")
    # creation of the event of the avalanche in a data format
    event_avalanche = datetime.datetime(int(splitted_date[0]), int(splitted_date[1]), int(splitted_date[2]), int(hours), int(min))
    # calculation of the hour before the avalanche (exactly 1h)
    hour_before_avalanche = event_avalanche - datetime.timedelta(hours=12)
    # conversion into format
    hour_before_avalanche = str(hour_before_avalanche)
    # now hour_before_avalanche is in the format : YYY-MM-DD HH:MM:SS
    # we split regarding the space which means we have now two chains : date and time
    diff = hour_before_avalanche.split(" ")
    # we split the chain which contains the date
    first_measurement_date = diff[0].split("-")
    # we split the chain which contains the time
    first_measurement_time = diff[1].split(":")

    # initial time for the measurements
    first_measurement = datetime.datetime(int(first_measurement_date[0]), int(first_measurement_date[1]), int(first_measurement_date[2]), int(first_measurement_time[0]), int(first_measurement_time[1]))
    # increment of 30 minutes
    increment = datetime.timedelta(minutes=30)

    # number of measurements we want
    nb_measurements = 25  # for 12 hours
    # List initialisation for time measurements
    time_measurements = []
    # Current time measurement initialisation
    current_measurement = first_measurement

    for _ in range(nb_measurements):
        # Adding the time to the list
        time_measurements.append(current_measurement.strftime("%Y-%m-%d-%H:%M"))
        # Going to the next time measurement
        current_measurement += increment

    # all the time are in time_measurements list and follow the format : YYYY-MM-DD-HH:MM
    for t in time_measurements:
        new_time = t.split("-")
        # we split regarding the character ":" to have the time
        new_hour = new_time[3].split(":")
        # adding the time for each measurement in the list
        measurements.append(new_time[0] + '-' + new_time[1] + '-' + new_time[2] + 'T' + new_hour[0] + ':' + new_hour[1] + ':00.000000Z')

    for i in range(nb_measurements):
        df = query("select * from 'imis' WHERE station_code = '" + station + "' and measure_date in '" + measurements[
            i] + "' order by measure_date")
        res = df.to_string()
        info = res.split()
        RSWR_30MIN_MEAN_12H_values.append(float(info[26]))

    # calcultes and returns radiation mean over last hour
    return statistics.mean(RSWR_30MIN_MEAN_12H_values)

# function that calculates the humidity mean value for the last hour before the event (avalanche)
def humidityMean(date, hours, min, station):
    # will be the list with all different times we need for the measurements
    measurements = []
    # date is in the format : YYYY-MM-DD
    splitted_date = date.split("-")
    # creation of the event of the avalanche in a data format
    event_avalanche = datetime.datetime(int(splitted_date[0]), int(splitted_date[1]), int(splitted_date[2]), int(hours), int(min))
    # calculation of the hour before the avalanche (exactly 1h)
    hour_before_avalanche = event_avalanche - datetime.timedelta(hours=1)
    # conversion into format
    hour_before_avalanche = str(hour_before_avalanche)
    # now hour_before_avalanche is in the format : YYY-MM-DD HH:MM:SS
    # we split regarding the space which means we have now two chains : date and time
    diff = hour_before_avalanche.split(" ")
    # we split the chain which contains the date
    first_measurement_date = diff[0].split("-")
    # we split the chain which contains the time
    first_measurement_time = diff[1].split(":")

    # initial time for the measurements
    first_measurement = datetime.datetime(int(first_measurement_date[0]), int(first_measurement_date[1]), int(first_measurement_date[2]), int(first_measurement_time[0]), int(first_measurement_time[1]))
    # increment of 30 minutes
    increment = datetime.timedelta(minutes=30)

    # number of measurements we want
    nb_measurements = 3  # for 1 hour
    # List initialisation for time measurements
    time_measurements = []
    # Current time measurement initialisation
    current_measurement = first_measurement

    for _ in range(nb_measurements):
        # Adding the time to the list
        time_measurements.append(current_measurement.strftime("%Y-%m-%d-%H:%M"))
        # Going to the next time measurement
        current_measurement += increment

    # all the time are in time_measurements list and follow the format : YYYY-MM-DD-HH:MM
    for t in time_measurements:
        new_time = t.split("-")
        # we split regarding the character ":" to have the time
        new_hour = new_time[3].split(":")
        # adding the time for each measurement in the list
        measurements.append(new_time[0] + '-' + new_time[1] + '-' + new_time[2] + 'T' + new_hour[0] + ':' + new_hour[1] + ':00.000000Z')

    for i in range(nb_measurements):
        df = query("select * from 'imis' WHERE station_code = '" + station + "' and measure_date in '" + measurements[
            i] + "' order by measure_date")
        res = df.to_string()
        info = res.split()
        RH_30MIN_MEAN_1H_values.append(float(info[25]))

    # calcultes and returns humidity mean over last hour
    return statistics.mean(RH_30MIN_MEAN_1H_values)

# function that calculates the wind velocity mean value for the last day before the event (avalanche)
def windVelocityMean(date, hours, min, station):
    # will be the list with all different times we need for the measurements
    measurements = []
    # date is in the format : YYYY-MM-DD
    splitted_date = date.split("-")
    # creation of the event of the avalanche in a data format
    event_avalanche = datetime.datetime(int(splitted_date[0]), int(splitted_date[1]), int(splitted_date[2]), int(hours), int(min))
    # calculation of the day before the avalanche (exactly 24h)
    day_before_avalanche = event_avalanche - datetime.timedelta(days=1)
    # conversion into format
    day_before_avalanche = str(day_before_avalanche)
    # now day_before_avalanche is in the format : YYY-MM-DD HH:MM:SS
    # we split regarding the space which means we have now two chains : date and time
    diff = day_before_avalanche.split(" ")
    # we split the chain which contains the date
    first_measurement_date = diff[0].split("-")
    # we split the chain which contains the time
    first_measurement_time = diff[1].split(":")

    # initial time for the measurements
    first_measurement = datetime.datetime(int(first_measurement_date[0]), int(first_measurement_date[1]), int(first_measurement_date[2]), int(first_measurement_time[0]), int(first_measurement_time[1]))
    # increment of 30 minutes
    increment = datetime.timedelta(minutes=30)

    # number of measurements we want
    nb_measurements = 49  # for 24 hours
    # List initialisation for time measurements
    time_measurements = []
    # Current time measurement initialisation
    current_measurement = first_measurement

    for _ in range(nb_measurements):
        # Adding the time to the list
        time_measurements.append(current_measurement.strftime("%Y-%m-%d-%H:%M"))
        # Going to the next time measurement
        current_measurement += increment

    # all the time are in time_measurements list and follow the format : YYYY-MM-DD-HH:MM
    for t in time_measurements:
        new_time = t.split("-")
        # we split regarding the character ":" to have the time
        new_hour = new_time[3].split(":")
        # adding the time for each measurement in the list
        measurements.append(new_time[0] + '-' + new_time[1] + '-' + new_time[2] + 'T' + new_hour[0] + ':' + new_hour[1] + ':00.000000Z')

    for i in range(nb_measurements):
        df = query("select * from 'imis' WHERE station_code = '" + station + "' and measure_date in '" + measurements[
            i] + "' order by measure_date")
        res = df.to_string()
        info = res.split()
        VW_30MIN_MEAN_1D_values.append(float(info[21]))

    # returns the wind velocity mean value
    return statistics.mean(VW_30MIN_MEAN_1D_values)

# function which given the wind velocity mean, gives a value according to it :
# if mean < 5 : 0
# else : 1
def windVelocityValue(date, hours, min, station):
    wind_mean = windVelocityMean(date, hours, min, station)
    # checking if the wind velocity mean during last day is higher than 5m/s
    if wind_mean < 5:
        return 0
    else:
        return 1

'''---------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------- CODE ---------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------'''
# open the original dataset with the avalanches
with open('super_small_dataset_test.csv', "r", encoding='utf-8-sig') as File:
    reader = csv.reader(File, delimiter=';')
    # store all the data in the corresponding lists
    for count, line in enumerate(reader, 1):
        if count != 1:
            print(line)
            triggerDateTime.append(line[0])
            coordX.append(line[1])
            coordY.append(line[2])
            startZoneElevation.append(line[3])
            startZoneAspect.append(line[4])
            fractureThicknessMean.append(line[5])
            size.append(line[6])
            lat.append(line[7])
            lon.append(line[8])
            IMIScode.append(line[9])
            IMISlat.append(line[10])
            IMISlon.append(line[11])
            # new_tDT stands for new trigger Date Time
            new_tDT = line[0].split(" ")
            # date is only the day (day/month/year) when the avalanche happened (time removed from triggerDateTime)
            date = new_tDT[0]
            # hour is only the time when the avalanche happened (day removed from triggerDateTime)
            hour = new_tDT[1]
            # split the date to change into the format needed to make requests on datawarehouse
            new_date = date.split("/")
            right_date = new_date[2] + '-' + new_date[1] + '-' + new_date[0]
            datesonly.append(right_date)
            # split the time to change into the format need to make requests on datawarehouse
            new_time = hour.split(":")
            hoursonly.append(new_time[0])
            # we decided to always take the measure made before the event, except when it's HH:30 then we take the measurement at the exact same time
            if int(new_time[1]) >= 30:
                mtime = 'T' + new_time[0] + ':30:00.000000Z'
                minutesonly.append("30")
            else:
                mtime = 'T' + new_time[0] + ':00:00.000000Z'
                minutesonly.append("00")
            measure = right_date + mtime
            measured_time.append(measure)

triggerDateTime = measured_time
# print(triggerDateTime[9])

# makes requests regarding the info from the avalanches dataset as well as the time defined for the measurement
for i in range(len(triggerDateTime)):
    print("Requests for avalanche n°" + str(i+1) + " are being made")
    print("select * from 'imis' WHERE station_code = '" + IMIScode[i] + "' and measure_date in '" + measured_time[i] + "' order by measure_date")
    df = query("select * from 'imis' WHERE station_code = '" + IMIScode[i] + "' and measure_date in '" + measured_time[i] + "' order by measure_date")
    # adding the new snow
    print("select * from 'imis_snowpack' WHERE station_code = '" + IMIScode[i] + "' and measure_date in '" + measured_time[
        i] + "' order by measure_date")
    df2 = query("select * from 'imis_snowpack' WHERE station_code = '" + IMIScode[i] + "' and measure_date in '" + measured_time[
        i] + "' order by measure_date")
    # results from the requests
    res = df.to_string()
    res2 = df2.to_string()
    # split to have each parameter/value
    info = res.split()
    info2 = res2.split()
    # put the info from the requests in lists
    station_code.append(info[17])
    measure_date.append(info[18])
    measure_time.append(info[19])
    hyear.append(info[20])
    VW_30MIN_MEAN.append(info[21])
    VW_30MIN_MAX.append(info[22])
    DW_30MIN_MEAN.append(info[23])
    TA_30MIN_MEAN.append(info[24])
    RH_30MIN_MEAN.append(info[25])
    RSWR_30MIN_MEAN.append(info[26])
    HS.append(info[27])
    TS0_30MIN_MEAN.append(info[28])
    TS25_30MIN_MEAN.append(info[29])
    TS50_30MIN_MEAN.append(info[30])
    TS100_30MIN_MEAN.append(info[31])
    TSS_30MIN_MEAN.append(info[32])
    DW_30MIN_SD.append(info[33])
    HN_1D.append(info2[15])
    HN_12H.append(info2[16])
    HN_6H.append(info2[17])
    RSWR_30MIN_MEAN_12H.append(radiationMean(datesonly[i], hoursonly[i], minutesonly[i], IMIScode[i]))
    RH_30MIN_MEAN_1H.append(humidityMean(datesonly[i], hoursonly[i], minutesonly[i], IMIScode[i]))
    VW_30MIN_MEAN_1D.append(windVelocityMean(datesonly[i], hoursonly[i], minutesonly[i], IMIScode[i]))
    VW_VALUE.append(windVelocityValue(datesonly[i], hoursonly[i], minutesonly[i], IMIScode[i]))

print("longueur radiation : " + str(len(RSWR_30MIN_MEAN_12H)))
print("longueur humidity : " + str(len(RH_30MIN_MEAN_1H)))
print("longueur wind velocity : " + str(len(VW_30MIN_MEAN_1D)))
# put all the information given by the IMIS in a DataFrame it's possible to remove the parameters that are not needed
# in the following line, and it's also possible to change the order
data = pd.DataFrame({col1: triggerDateTime, col2: coordX, col3: coordY, col4: startZoneElevation, col5: startZoneAspect, col6: fractureThicknessMean, col7: size, col8: lat, col9: lon, col10: IMIScode, col11: IMISlat, col12: IMISlon, col13: measure_date, col14: hyear, col15: VW_30MIN_MEAN, col16: VW_30MIN_MAX, col17: DW_30MIN_MEAN, col18: TA_30MIN_MEAN, col19: RH_30MIN_MEAN, col20: RSWR_30MIN_MEAN, col21: HS, col22: TS0_30MIN_MEAN, col23: TS25_30MIN_MEAN, col24: TS50_30MIN_MEAN, col25: TS100_30MIN_MEAN, col26: TSS_30MIN_MEAN, col27: DW_30MIN_SD, col28: HN_1D, col29: HN_12H, col30: HN_6H, col31: RSWR_30MIN_MEAN_12H, col32: RH_30MIN_MEAN_1H, col33: VW_30MIN_MEAN_1D, col34: VW_VALUE})
# write all the information given into a new Excel file with the info from the avalanches
data.to_excel("generated_dataset.xlsx", sheet_name="sheet1", index=False)