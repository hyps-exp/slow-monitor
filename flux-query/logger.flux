from (bucket: "logger")
  |> range(start: -1h)

// |> filter(fn: (r) => r._measurement == "bgotemp" and r._field == "value")
// |> keep(columns: ["_time", "_field", "_value", "channel"])
// |> drop(columns: ["dest_bucket", "environment", "host"])
// |> sample(n: 10, pos: 0)
// |> aggregateWindow(column: "_value", fn: mean, every: 2h)
