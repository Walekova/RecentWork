#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType


def transaction_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- description: string (nullable = true)
    |-- amount: string (nullable = true)
    |-- timestamp: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("amount", StringType(), True),
        StructField("description", StringType(), True),
    ])


def purchase_event_schema():
    return transaction_event_schema()

def add_money_event_schema():
    return transaction_event_schema()

def guild_membership_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- guild_name: string (nullable = true)
    |-- timestamp: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("guild_name", StringType(), True),
    ])

def cancel_membership_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- cancel_reason: string (nullable = true)
    |-- timestamp: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("cancel_reason", StringType(), True),
    ])

def message_event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- message: string (nullable = true)
    |-- timestamp: string (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("message_post", StringType(), True),
    ])

@udf('boolean')
def is_purchase(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if 'purchase' in event['event_type']:
        return True
    return False

@udf('boolean')
def is_add_money(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'add_money':
        return True
    return False

@udf('boolean')
def is_transaction(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'add_money' or 'purchase' in event['event_type']:
        return True
    return False


@udf('boolean')
def is_join_guild(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'join_guild':
        return True
    return False

@udf('boolean')
def is_guild_member(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'join_guild':
        return True
    return False

@udf('boolean')
def is_cancel_member(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'cancel_membership':
        return True
    return False

@udf('boolean')
def is_message(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] == 'mensaje':
        return True
    return False


def main():
    """
    main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "game_events") \
        .load()

    purchases = raw_events \
        .filter(is_purchase(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          purchase_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    add_money = raw_events \
        .filter(is_add_money(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          add_money_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    guild_membership = raw_events \
        .filter(is_guild_member(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          guild_membership_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    cancel_membership = raw_events \
        .filter(is_cancel_member(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          cancel_membership_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    messages2 = raw_events \
        .filter(is_message(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          message_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    transactions = raw_events \
        .filter(is_transaction(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          transaction_event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')
    
    sink_purchases = purchases \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_purchases") \
        .option("path", "/tmp/purchases") \
        .trigger(processingTime="120 seconds") \
        .start()

    sink_add_money = add_money \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_add_money") \
        .option("path", "/tmp/add_money") \
        .trigger(processingTime="120 seconds") \
        .start()

    sink_guild_membership = guild_membership \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_guild_membership") \
        .option("path", "/tmp/guild_membership") \
        .trigger(processingTime="120 seconds") \
        .start()

    sink_cancel_membership = cancel_membership \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_cancel_membership") \
        .option("path", "/tmp/cancel_membership") \
        .trigger(processingTime="120 seconds") \
        .start()
    
    sink_messages2 = messages2 \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_messages2") \
        .option("path", "/tmp/messages2") \
        .trigger(processingTime="120 seconds") \
        .start()
    
    sink_transactions = transactions\
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_transactions") \
        .option("path", "/tmp/transactions") \
        .trigger(processingTime="120 seconds") \
        .start()
    
    sink_purchases.awaitTermination()
    sink_add_money.awaitTermination()
    sink_guild_membership.awaitTermination()
    sink_cancel_membership.awaitTermination()
    #sink_messages.awaitTermination()
    sink_messages2.awaitTermination()
    sink_transactions.awaitTermination()
    
if __name__ == "__main__":
    main()
