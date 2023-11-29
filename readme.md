# Instructions
### To run 
```sh
git clone https://github.com/hidara2000/fast_sensor_stream.git

cd fast_sensor_stream
pip install -r requirements.txt

bokeh serve --show bokeh_stream
```

#### 1 plot @ 400Hz
https://github.com/hidara2000/fast_sensor_stream/assets/15170494/89822124-09c2-4aed-bc7a-2644c3e27b70

    
#### 6 plots @ 67Hz each
https://github.com/hidara2000/fast_sensor_stream/assets/15170494/540b1502-6797-492d-904d-713d164ceb43


### NOTES
- Still a work in progress
- The delay slider allows for manually adding a delay needed for the plots to update. In WSL, with an i7, a single plot with two lines is comfortable at 400Hz but may miss 1 reading ever 2000 updates. Reduce to 200Hz for a more stable performance. For 6 plots, 7 lines 67Hz works well
- for real data just replace the SensorProducer class with something similar to below
    ``` python
    class SensorProducer(Thread):
        def __init__(self, details: SensorDetails, sensor_is_reading: Event) -> None:
            Thread.__init__(self)
            self.details = details
            self.sensor_is_reading = sensor_is_reading

            self.fn = details.fn
            self.data = {'x': [0],'y': [0]}

            self.details.data_q.append(self.data)

        def run(self):
            while True:
                if self.sensor_is_reading.is_set():
                    time.sleep(self.details.delay_q.latest())

                    self.details.data_q.append(self.fn())

        def read(self):
            return self.details.data_q.latest()
        
        def current_milli_time(self, start_time=0):
            return round(time.time() * 1000) - start_time
    ```
    and adjust the code in main so that it just sends the sensor read function and adjust the dictionary to reflect title, legend values etc

    ### Sample sensor read function
    ```python
    def get_latest_sensor_data(self):
        """Some code that reads sensor data and returns returns a dict formatted as follows

        For a single line

            data = {'x': [<x_latest_sensor_reading>],'y': [<y_latest_sensor_reading>]}
            
            or multiple lines in a plot eg gyro or accelerometer
            
            
            data = {
                'x':  [<x_latest_sensor_reading>]
                'y':  [<y_latest_sensor_reading_0>],
                'y1': [<y2_latest_sensor_reading_1]>,
                'y2': [<y3_latest_sensor_reading_2]>,
                'y3': [<y4_latest_sensor_reading_3]>,
                                ...
                'yn': [<y_latest_sensor_reading_n]>
            }
            
            this will plot n lines in a single plot. Note all x & y values are in a list eg {'x': [0.123],'y': [12.45]}


            return data
        """
    ```

    ### Sample sensor SensorDetails
    ```python
    class SensorDetails:
        fn: Callable
        legend: Dict[str, str]
        title: str
        # a slight delay is needed for high frequency sensor data (>100Hz)
        delay_q: RollingStack
        data_q: RollingStack
    
    ```

    ### Sample main
    ``` python
    def main():
        sensor_speed_slider_value = 0.0025

        delay_queue = RollingStack(1, sensor_speed_slider_value)
        sensor_is_reading = Event()
        sensor_is_reading.set()

        my_signal = (
            SensorDetails(
                get_latest_sensor_data,
                {"y": "Sensor Reading"},
                "Proximity Sensor Readings",
                delay_queue,
                RollingStack(3),
            ),
        )

        main_page = BokehPage(
            LayoutDefaults(delay_queue, 
            sensor_speed_slider_value=sensor_speed_slider_value),
            sensor_is_reading,
        )

        producer = SensorProducer(get_latest_sensor_data, sensor_is_reading)
        plt = BokehPlot(main_page, my_signal)
        consumer = SensorConsumer(plt, producer, sensor_is_reading)

        producer.start()
        consumer.start()

        main_page.add_plots([plt])
    
    ```
