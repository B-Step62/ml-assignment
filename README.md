# ML Assignment
Please implement a translation inference service that runs on Kubernetes and provides a RESTful API on port 9527.

The translation model is `M2M100`, and the example can be found in `app/translation_example.py`.

You should first fork this repository, and then send us the code or the url of your forked repository via email. 

**Please do not submit any pull requests to this repository.**


## Delivery
- **app/Dockerfile**: To generate an application image
- **k8s/deployment.yaml**: To deploy image to Kubernetes
- Other necessary code

### [[Note from author]]
As I have no personal kubernetes environment, I built my solution with docker-compose and translate it to kubernetes definition using [Kompose](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/), but haven't verify it if really works or not on k8s. To reproduce original result with docker-compose, please run `docker compose up` on the top directory.

## Input/Output

When you execute this command:
```bash
curl --location --request POST 'http://127.0.0.1:9527/translation' \
--header 'Content-Type: application/json' \
--data-raw '{
    "payload": {
        "fromLang": "en",
        "records": [
            {
                "id": "123",
                "text": "Life is like a box of chocolates."
            }
        ],
        "toLang": "ja"
    }
}'
```

Should return:
```bash
{
   "result":[
      {
         "id":"123",
         "text":"人生はチョコレートの箱のようなものだ。"
      }
   ]
}
```

## Bonus points
- Clean code
- Scalable architecture
- Good inference performance
- Efficient CPU/GPU utilization
