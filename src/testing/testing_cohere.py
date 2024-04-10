import cohere

api_key='A311TIPYTiHm9pDyDvkhlQ69DAQb5qXrTU4aLRQ9'

print("Hello")
co = cohere.Client(
    api_key=api_key,
)


if True:
    stream = co.chat_stream(
        message="Tell me a short story"
    )

    for event in stream:
        if event.event_type == "text-generation":
            print(event.text, end='')
