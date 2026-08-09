FROM public.ecr.aws/lambda/python:3.12-arm64
COPY pyproject.toml LICENSE requirements-lambda-demo.txt ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements-lambda-demo.txt && pip install --no-cache-dir --no-deps .
ENV RECALLOPS_MODE=demo
CMD ["recallops.lambda_handler.handler"]
