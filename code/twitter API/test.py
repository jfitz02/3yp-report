import data_collator
import requests
import model_api

def main():
    collator = data_collator.DataCollator("pass.secret")
    model = model_api.TweetProcessor(4)

    tweet = collator.get_tweet(1607738076985495554)

    media_type = None
    url = ""
    if "media" in tweet.extended_entities:
        media_type = tweet.extended_entities["media"][0]["type"]
        if tweet.extended_entities["media"][0]["type"] == "photo":
            url = tweet.extended_entities["media"][0]["media_url"]
        elif tweet.extended_entities["media"][0]["type"] == "video":
            variants = tweet.extended_entities["media"][0]["video_info"]["variants"]
            # get variant that is mp4
            url = ""
            for variant in variants:
                if variant["content_type"] == "video/mp4":
                    url = variant["url"]
                    break

    if media_type is None:
        print("NO MEDIA")
        prediction = model.get_topic(tweet.full_text)
        return
    elif media_type == "photo":
        print("GOT PHOTO")
        prediction = model.get_topic(tweet.full_text, image_url=url)
    elif media_type == "video":
        print("GOT VIDEO")
        prediction = model.get_topic(tweet.full_text, audio_url=url)
    print(prediction)



main()