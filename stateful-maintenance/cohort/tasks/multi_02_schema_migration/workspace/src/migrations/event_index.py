def apply(connection):
    connection.execute('CREATE INDEX idx_events_timestamp ON events(timestamp)')
