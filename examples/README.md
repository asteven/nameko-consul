### Run examples

```
nameko run --config ./config.yaml service
```

### Poke it

```
curl http://127.0.0.1:8001/reset-count

curl http://127.0.0.1:8001/increment-count
curl http://127.0.0.1:8001/increment-count
```


### Fire event

```
consul event -name=fire some-payload
```
