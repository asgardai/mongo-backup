# MongoDB S3 Backup Docker image

Based on https://github.com/agmangas/mongo-backup-s3.
With some modification from https://gist.github.com/caraboides/7679bb73f4f13e36fc2b9dbded3c24c0
And simplification in Dockerfile :)

...

Docker image that performs periodic backups on a MongoDB database and then uploads the results to Amazon S3.

Based on the [dbader/schedule](https://github.com/dbader/schedule) Python scheduling package.

## Configuration

The following table describes the available configuration environment variables.

Name | Description | Default
--- | --- | ---
`MONGO_HOST` | MongoDB instance hostname | *Required*
`MONGO_PORT` | MongoDB database name | *Required*
`MONGO_DB` | MongoDB database name | *Required*
`MONGO_USERNAME` | MongoDB database name | *Required*
`MONGO_PASSWORD` | MongoDB database name | *Required*
`S3_FOLDER` | Amazon S3 bucket name | *Required*
`AWS_ACCESS_KEY_ID` | Amazon AWS access key | *Required*
`AWS_SECRET_ACCESS_KEY` | Amazon AWS secret | *Required*
`BACKUP_INTERVAL` | Interval between each backup (days) | `1`
`BACKUP_TIME` | Hour of the day at which the backup will be executed | `2:00`
`DATE_FORMAT` | Date format string used as the suffix of the backup filename | `%Y%m%d-%H%M%S`
`FILE_PREFIX` | Prefix of the backup filename | `backup-`

## Example

The following command starts a *mongo-s3-backup* container that will stay in the background uploading backups of the *testdb* database on the *my-mongo-host* MongoDB instance every day at 2:00. The backups will be uploaded to an S3 bucket named *my-s3-bucket*:

```
docker run -d --name mongo_backups \
	-e MONGO_HOST=localhost -e MONGO_PORT=27017 \
	-e MONGO_USERNAME=root -e MONGO_PASSWORD=test \
	-e MONGO_DB=data \
	-e S3_FOLDER=s3://asgard-db-backup/mongo/ \
	-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
	-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	-e BACKUP_INTERVAL=1  \
	-e BACKUP_TIME=19:00 \
	asgard/mongo-backup-s3

docker run -d --name mongo_backups --net asgardapi_asgard_net --env-file .env \
	asgard/mongo-backup-s3

```
