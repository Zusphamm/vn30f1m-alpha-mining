# Data format

`vn30alpha.data.load(path)` reads a parquet or csv file of VN30F1M (front-month VN30 index future) bars.

| Column | Type | Note |
|--------|------|------|
| `time_vn` | datetime | bar open time in Vietnam time (tz-aware Asia/Ho_Chi_Minh or naive local) |
| `open`, `high`, `low`, `close` | float | index points, continuous front-month series |
| `volume` | int / float | contracts |

- Bar size: 10 minutes. Only the 24 continuous-session bars are kept: 09:00 .. 11:20 and 13:00 .. 14:20.
- The published results used data from 2018-08-13 09:00 to 2026-10-28 14:40.
- No data ships with this repository.

## Related

- [Methodology](methodology.md)
- [README](../README.md)
