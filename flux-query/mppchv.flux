import "strings"

from(bucket: "mppchv")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "mppchv")
//   // |> map(fn: (r) => ({ r with mppchv: strings.toUpper(v: r.mppchv) }))
  |> sort(columns: ["_time"], desc: true)
  |> unique(column: "_field")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> group(columns: [])
 |> sort(columns: ["ip", "channel"])
// //  |> keep(columns: ["_time", "mppchv", "cmon", "cset", "pol"])
  |> keep(columns: ["_time", "ip", "channel", "name", "vset", "vmon", "iset", "imon", "status", "temp", "trip"])
  