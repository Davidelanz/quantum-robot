# Glossary

```{glossary}
quantum-like model
  A computational model that represents normalized input sequences with quantum
  states and operations. In this project, a model encodes one qubit per input
  dimension over a fixed number of samples, applies an optional query
  transformation, and obtains an output by measuring the resulting circuit. The
  term describes the model's mathematical and computational structure; it does
  not imply that the surrounding robot or simulator is a quantum physical system.

qUnit
  A Redis-connected processing unit implemented by {class}`qrobot_qunits.QUnit`.
  It periodically reads normalized values from upstream units, encodes them with
  a quantum-like model over a temporal window, applies a query, and publishes a
  normalized burst. A qUnit can serve a perceptual or cognitive role depending on
  its inputs and purpose in a qBrain.

qBrain
  A network of sensorial units, qUnits, and actuators connected through their
  Redis inputs and outputs. A qBrain is an architectural concept rather than a
  single Python class: the application constructs and connects its constituent
  units for a particular robot or research scenario.

burst
  A rule that converts a qUnit's decoded measurement state into a normalized
  scalar output. The supplied {class}`qrobot.bursts.ZeroBurst` and
  {class}`qrobot.bursts.OneBurst` strategies express how strongly the measured
  bit string resembles the all-zero or all-one state, respectively.

query
  A normalized target vector, with one value per model dimension, used to change
  the measurement basis after inputs have been encoded. An input matching the
  query is mapped toward the all-zero state before measurement. The selected
  burst strategy determines how that measured state becomes the qUnit output.

temporal window
  The sequence of samples accumulated by a quantum-like model before it is
  queried, measured, and cleared. Its length is the model's ``tau`` value; for a
  qUnit sampled every ``sampling_period`` seconds, the nominal window duration is
  ``tau * sampling_period`` seconds.

sensorial unit
  A {class}`qrobot_qunits.SensorialUnit` that periodically publishes one
  normalized sensor reading to Redis. It forms an input boundary between a
  sensor or simulated observation and the qBrain.

perceptual unit
  A qUnit whose upstream inputs are sensorial units and whose burst represents a
  detected feature or perceptual condition over a temporal window. This is a
  functional role in a qBrain, not a separate Python class.

cognitive unit
  A qUnit that integrates outputs from perceptual or other qUnits to represent a
  higher-level condition or decision. This is a functional role in a qBrain, not
  a separate Python class.

actuator
  A {class}`qrobot_qunits.ActuatorUnit` that reads the latest bursts from one or
  more qUnits, combines them into a normalized value, applies its activation
  rule, and publishes the result for robot or simulator behavior to consume.
  Actuators translate qBrain outputs into control signals; they do not directly
  model the mechanics of a physical device.
```
