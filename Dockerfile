FROM public.ecr.aws/lambda/python:3.9

COPY hello_world/. ./

RUN python3.9 -m pip install -r requirements.txt

CMD ["app.lambda_handler"]
