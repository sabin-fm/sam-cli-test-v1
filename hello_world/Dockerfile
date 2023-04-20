FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY service_account.json ${LAMBDA_TASK_ROOT}
COPY custom_encoder.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]