import ppk2_api.ppk2_api
import time

ppk2_test = ppk2_api.ppk2_api.PPK2_API(port = "/dev/ttyACM0")
ppk2_test.get_modifiers()
ppk2_test.use_source_meter()  # set source meter mode
ppk2_test.set_source_voltage(4000)  # set source voltage in mV
ppk2_test.toggle_DUT_power("ON")

while True:
    ppk2_test.start_measuring()
    time.sleep(1)
    ppk2_test.stop_measuring()

    read_data = ppk2_test.get_data()
    if read_data != b'':
        samples = ppk2_test.get_samples(read_data)
        average_current = sum(samples)/len(samples)
        print(f"Average of {len(samples)} samples is: {average_current}uA")