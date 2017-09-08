# Standard SQL
SELECT
  TIMESTAMP_SECONDS(timestamp) AS timestamp,
  DATE(TIMESTAMP_SECONDS(timestamp)) AS date,
  exchange,
  coin,
  cast(price as float64) as price,
  currency,
  cast(volume as float64) as volume,
  TIMESTAMP_SECONDS(req_timestamp) AS req_timestamp
FROM
  `transaction_log.temp*`
WHERE
  _TABLE_SUFFIX BETWEEN "0"
  AND "9"
GROUP BY
  1,
  2,
  3,
  4,
  5,
  6,
  7,
  8
HAVING
  date = CURRENT_DATE()
ORDER BY
  timestamp