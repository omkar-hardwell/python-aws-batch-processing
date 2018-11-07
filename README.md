# Batch processing using AWS

**Use Case**<br/>

![Workflow](images/python-aws-batch-processing.jpg)


1) User can upload CSV using flask web application
2) Application logic will create a batches
3) Batches stored into Amazon S3 bucket
3) Once any batch arrives in S3 bucket, lambda function invokes per batch basis
4) Lambda process the batch and store data to Amazon RDS
