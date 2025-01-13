## Start Chroma

`sudo docker run -d -p 8000:8000 chromadb/chroma`

## Testing

### Integration
`poetry run pytest disrupt_arch/tests/integration/test_escalation_workflow.py --log-cli-level=INFO`