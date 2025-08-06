SELECT JSON_ARRAYAGG(
         JSON_OBJECT(
           'tablespace' VALUE tspace,
           'tot_ts_size' VALUE tot_ts_size,
           'used_ts_size' VALUE used_ts_size,
           'free_ts_size' VALUE free_ts_size,
           'used_pct' VALUE used_pct,
           'free_pct' VALUE free_pct,
           'warning' VALUE warning
         )
       ) AS tablespace_usage
FROM (
  SELECT df.tablespace_name tspace,
         ROUND(SUM(fs.bytes_free + fs.bytes_used) / 1024 / 1024, 2) tot_ts_size,
         ROUND(SUM(fs.bytes_used) / 1024 / 1024, 2) used_ts_size,
         ROUND(SUM(fs.bytes_free) / 1024 / 1024, 2) free_ts_size,
         ROUND(SUM(fs.bytes_used) * 100 / SUM(fs.bytes_free + fs.bytes_used)) used_pct,
         ROUND(SUM(fs.bytes_free) * 100 / SUM(fs.bytes_free + fs.bytes_used)) free_pct,
         DECODE(SIGN(SUM(ROUND(((fs.bytes_free + fs.bytes_used) - fs.bytes_free) * 100 / (fs.bytes_free + fs.bytes_used))) - 80), 1, '!ALERT', '') warning
  FROM SYS.V_$TEMP_SPACE_HEADER fs
  JOIN dba_temp_files df ON fs.tablespace_name = df.tablespace_name AND fs.file_id = df.file_id
  GROUP BY df.tablespace_name

  UNION

  SELECT df.tablespace_name tspace,
         df.bytes / (1024 * 1024) tot_ts_size,
         ROUND((df.bytes - SUM(fs.bytes)) / (1024 * 1024)) used_ts_size,
         SUM(fs.bytes) / (1024 * 1024) free_ts_size,
         ROUND((df.bytes - SUM(fs.bytes)) * 100 / df.bytes) used_pct,
         ROUND(SUM(fs.bytes) * 100 / df.bytes) free_pct,
         DECODE(SIGN(ROUND((df.bytes - SUM(fs.bytes)) * 100 / df.bytes) - 80), 1, '!ALERT', '') warning
  FROM dba_free_space fs
  JOIN (
    SELECT tablespace_name, SUM(bytes) bytes
    FROM dba_data_files
    GROUP BY tablespace_name
  ) df ON fs.tablespace_name = df.tablespace_name
  GROUP BY df.tablespace_name, df.bytes

  UNION

  SELECT tablespace_name tspace,
         1 tot_ts_size,
         1 used_ts_size,
         0 free_ts_size,
         100 used_pct,
         0 free_pct,
         '!' warning
  FROM dba_data_files
  GROUP BY tablespace_name
  MINUS
  SELECT tablespace_name tspace,
         1 tot_ts_size,
         1 used_ts_size,
         0 free_ts_size,
         100 used_pct,
         0 free_pct,
         '!' warning
  FROM dba_free_space
  GROUP BY tablespace_name
)
ORDER BY free_ts_size;
