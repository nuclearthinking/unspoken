# UNSPOKEN

Convert audio to text-conversation separeted by speakers.


Start with this command. 
```bash
docker-compose up -d
```


Upload file 
```bash
curl --location '0.0.0.0:8000/upload/audio' \
--form 'file=@"/home/user/audio_file.m4a"'
```
In response you will recieve task_id 

Then call endpoint with recieved task_id, to see current task state 
```bash
curl --location '0.0.0.0:8000/task/17'
```
After task were finished processing, it change status to `completed` and result will contain array of transcribed messages with data like timestamps and speaker. 

Current accuracy of STT and Speaker Diarization is still not that good, but still could be good enaugh for some purposes. 

based on [faster-whisper](https://github.com/guillaumekln/faster-whisper) and NeMo 
