import "array"
import "strings"

///// InputDAC

input_dac_data = from(bucket: "vme-easiroc")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "input_dac")
  |> map(fn: (r) => ({
    module: int(v: r.module),
    ch: int(v: strings.replaceAll(v: r._field, t: "ch", u: "")),
    input_dac: r._value,
    _time: r._time
  }))
  |> group(columns: ["module", "ch"])
  |> last(column: "input_dac")
  |> keep(columns: ["module", "ch", "input_dac", "_time"])

///// PedeSup HG
pede_sup_hg_data = from(bucket: "vme-easiroc")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "pede_sup")
  |> filter(fn: (r) => r._field =~ /^hg_ch[0-9]{2}$/)
  |> map(fn: (r) => ({
    module: int(v: r.module),
    ch: int(v: strings.replaceAll(v: r._field, t: "hg_ch", u: "")),
    pede_sup_hg: r._value,
    _time: r._time
  }))
  |> group(columns: ["module", "ch"])
  |> last(column: "pede_sup_hg")
  |> keep(columns: ["module", "ch", "pede_sup_hg", "_time"])

///// PedeSup LG
pede_sup_lg_data = from(bucket: "vme-easiroc")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "pede_sup")
  |> filter(fn: (r) => r._field =~ /^lg_ch[0-9]{2}$/)
  |> map(fn: (r) => ({
    module: int(v: r.module),
    ch: int(v: strings.replaceAll(v: r._field, t: "lg_ch", u: "")),
    pede_sup_lg: r._value,
    _time: r._time
  }))
  |> group(columns: ["module", "ch"])
  |> last(column: "pede_sup_lg")
  |> keep(columns: ["module", "ch", "pede_sup_lg", "_time"])

joined1 = join(
  tables: {dac: input_dac_data, pede_hg: pede_sup_hg_data},
  on: ["module", "ch", "_time"]
)

join(
  tables: {joined: joined1, pede_lg: pede_sup_lg_data},
  on: ["module", "ch", "_time"]
)

|> group()
|> sort(columns: ["module", "ch"])