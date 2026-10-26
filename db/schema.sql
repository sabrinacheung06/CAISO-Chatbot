CREATE TABLE ingest_log (
  id bigserial PRIMARY KEY,
  source_url text,
  query_params jsonb,
  fetched_at timestamptz DEFAULT now(),
  row_count int
);

CREATE TABLE node (
  node_id text PRIMARY KEY,
  node_type text
);

CREATE TABLE lmp (
  ts_utc timestamptz NOT NULL,
  market text NOT NULL,
  node_id text NOT NULL REFERENCES node(node_id),
  lmp numeric, energy numeric, congestion numeric, loss numeric, ghg numeric,
  ingest_id bigint REFERENCES ingest_log(id),
  PRIMARY KEY (node_id, market, ts_utc)
);
