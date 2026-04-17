-- Enable Row Level Security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_pairs ENABLE ROW LEVEL SECURITY;

-- Create Policies based on pipeline_id context setting
CREATE POLICY isolate_documents ON documents
    USING (pipeline_id = current_setting('app.current_pipeline_id', true)::uuid);

CREATE POLICY isolate_chunks ON chunks
    USING (document_id IN (SELECT id FROM documents WHERE pipeline_id = current_setting('app.current_pipeline_id', true)::uuid));

CREATE POLICY isolate_runs ON pipeline_runs
    USING (pipeline_id = current_setting('app.current_pipeline_id', true)::uuid);

CREATE POLICY isolate_evals ON evaluations
    USING (run_id IN (SELECT id FROM pipeline_runs WHERE pipeline_id = current_setting('app.current_pipeline_id', true)::uuid));

CREATE POLICY isolate_training ON training_pairs
    USING (run_id IN (SELECT id FROM pipeline_runs WHERE pipeline_id = current_setting('app.current_pipeline_id', true)::uuid));