Original query for pulling dataset->dataset->(via)tool triplets.


```
select jtid.dataset_id as input_dataset, jtod.dataset_id as output_dataset,
jb.tool_id from job_to_input_dataset as jtid inner join job_to_output_dataset
as jtod on jtod.job_id = jtid.job_id inner join job as jb on jtid.job_id =
jb.id where jtid.dataset_id is not null order by jtid.dataset_id DESC limit 50;
```



Supplemental query we used for adding add upload left-hand leaf nodes.

```
select job.tool_id, jtod.dataset_id, job2.tool_id from job inner join
job_to_output_dataset as jtod on job.id = jtod.job_id inner join
job_to_input_dataset as jtid on jtod.dataset_id = jtid.dataset_id inner join
job as job2 on jtid.job_id = job2.id where job.tool_id = 'upload1';
```
