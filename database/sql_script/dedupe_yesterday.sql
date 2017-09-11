# Standard SQL
WITH
  max_timestamp AS(
  SELECT
    MAX(timestamp) as timestamp
  FROM
    `transaction_log.transaction*`
  WHERE
    _TABLE_SUFFIX IN (
    SELECT
      REGEXP_EXTRACT(MAX(table_id), r'(\d+)')
    FROM
      transaction_log.__TABLES__
    WHERE
      table_id LIKE "%transaction%"))

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
  date =DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND timestamp > (
  SELECT
    *
  FROM
    max_timestamp)
ORDER BY
  timestamp