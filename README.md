# Batch processing using AWS

**Use Case**<br/>

![Workflow](images/python-aws-batch-processing.jpg)


1) User can upload CSV using flask web application
2) Application logic will create a batches
3) Batches stored into Amazon S3 bucket
4) Once any batch arrives in S3 bucket, lambda function invokes per batch basis
5) Lambda process the batch and store data to Amazon RDS

**Amazon RDS (MySQL)**<br/>

Database : batch_processing<br/>
Table : release_region_restriction
```
create table release_region_restriction(
	id int(11) primary key auto_increment,
	release_id int(11) not null,
	region_code char(2) not null
);
```
