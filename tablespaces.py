
set lines 500
set pages 100
col tspace form a25 Heading "Tablespace"
col tot_ts_size form 99999999 Heading "Size (Mb)"
col free_ts_size form 99999999 Heading "Free (Mb)"
col used_ts_size form 99999999 Heading "Used (Mb)"
col used_pct form 99999 Heading "% Used"
col free_pct form 99999 Heading "% Free"
col warning form a10 Heading "Message"
break on report
compute sum label total of tot_ts_size on report
compute sum label total of used_ts_size on report
compute sum label total of free_ts_size on report
         (select  df.tablespace_name tspace
   ,       round(sum(fs.bytes_free + fs.bytes_used) / 1024 / 1024, 2) tot_ts_size
   ,       round(sum(fs.Bytes_used) / 1024 / 1024, 2)  used_ts_size
   ,       round(sum(fs.bytes_free) / 1024 / 1024, 2)  free_ts_size
   ,       round(sum(fs.Bytes_used ) * 100 / sum((fs.bytes_free + fs.bytes_used))) used_pct
   ,       round(sum(fs.Bytes_free ) * 100 / sum((fs.bytes_free + fs.bytes_used))) free_pct
   ,      decode(sign(sum(round(((fs.bytes_free + fs.bytes_used)-fs.bytes_free)*100/(fs.bytes_free + fs.bytes_used))) - 80), 1, '
   !ALERT', '') warning
   from   SYS.V_$TEMP_SPACE_HEADER fs
   ,      dba_temp_files df
   where fs.tablespace_name(+) = df.tablespace_name
     and fs.file_id(+) = df.file_id
     group by df.tablespace_name
     union
     SELECT df.tablespace_name tspace
     ,      df.bytes/(1024*1024) tot_ts_size
     ,      round((df.bytes-sum(fs.bytes))/(1024*1024)) used_ts_size
     ,      sum(fs.bytes)/(1024*1024) free_ts_size
     ,      round((df.bytes-sum(fs.bytes))*100/df.bytes) used_pct
     ,      round(sum(fs.bytes)*100/df.bytes) free_pct
     ,      decode(sign(round((df.bytes-sum(fs.bytes))*100/df.bytes) - 80), 1, '!ALERT', '') warning
     FROM dba_free_space fs
     , (select tablespace_name, sum(bytes) bytes
        from dba_data_files
           group by tablespace_name
              ) df
              WHERE fs.tablespace_name(+) = df.tablespace_name
              GROUP BY df.tablespace_name, df.bytes)
              union
              (select tablespace_name tspace,
              1,1,0 free_ts_size,100 used_pct,0 free_pct,'!' warning from dba_data_files
              group by tablespace_name
              minus
              select tablespace_name tspace,1,1,0 free_ts_size,100 used_pct,0 free_pct,'!' warning
              from dba_free_space
              group by tablespace_name)
              order by 4
              ;

