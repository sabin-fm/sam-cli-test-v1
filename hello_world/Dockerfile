FROM public.ecr.aws/lambda/python:3.9

COPY hello_world/requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY hello_world/lambda_function.py ${LAMBDA_TASK_ROOT}
COPY hello_world/service_account.json ${LAMBDA_TASK_ROOT}
COPY hello_world/custom_encoder.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
