# iCareCommunication

icarecommunication is a shared package to simplify the communication of the projects [iCare](https://github.com/Hadar-N/icare) and [iCareControl](https://github.com/Hadar-N/icarecontrol). It uses the MQTT protocol for communications, centralizing communication logic and shared constants.

The project is developed under the supervision of National Tsing Hua University.

## Structure

The package exports 2 modules:

* **game_shared** - exporting constants relevant for the iCare game and classes/structures for data needed for communication
* **mqtt_shared** - exporting the `ConnectionManager` and classes relevant for its usage

## ConnectionManager

The `ConnectionManager` is the main package in charge of the communication. It is implemented as a singleton, providing `initialize` and `get_instance` class methods for instance management, and instance methods for data and connection management (e.g. `publish_message`, `get_current_game_status`...).

The package supports two methods for reading messages:
(1) using a callback function during initialization
(2) retrieving messages from a queue based on device_id via `register_device` and `get_device_msg`.

To initialize the instance, use `MQTTInitialData` (used to store connection information) and `DEVICE_TYPE` (responsible for assigning specific topics) as follows:

```python
class MQTTInitialData:
    port: str
    host: str
    username: str
    password: str
class DEVICE_TYPE(str, Enum):
    GAME="game"
    CONTROL="control"

conn = ConnectionManager.initialize(init_data: MQTTInitialData, role: DEVICE_TYPE, logger: Logger, on_message: callable)
```


## Dependencies

This package depends on paho-mqtt for the communication.

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/)