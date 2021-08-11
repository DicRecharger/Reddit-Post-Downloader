import requests, re
import subprocess, os

videoToAudio_pattern = re.compile(r'DASH_[\d][\d][\d][\d]?')
video_pattern = re.compile(r'https?://v.redd.it/(?P<filename>[^\s]+)/') # we only need the filename here
image_pattern = re.compile(r'https?://i.redd.it/(?P<filename>[^\s]+).(?P<filetype>jpg|png|jpeg|gif)') # here we need the filename and the filetype

user_agent = {"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57"}

def download_reddit(url):
	r = requests.get(url, headers=user_agent)
	text = r.json()

	data = text[0]['data']['children'][0]['data']

	if data.get('is_video'):
		media = data.get('media')

		video_url = media['reddit_video']['fallback_url']
		filename_video = video_pattern.search(video_url).group('filename') + '_' # this _ is just so we can combine it with the audio later without any Permission Errors

		audio = False if media['reddit_video']['is_gif'] else True # if 'is_gif' is True, then the video does not have audio, so audio will be False

		if audio:
			audio_url = videoToAudio_pattern.sub('DASH_audio', video_url)
			filename_audio = filename_video + 'audio'

			download(video_url, filename_video)
			download(audio_url, filename_audio)
			return combine(filename_video, filename_audio)
		else:
			# [0:-1] will return the string without the last character, 
			# we need this because if the media is a "gif video", then there is no need for combining, and the _ will stay if we don't remove it
			return download(video_url, filename_video[0:-1]) 
		
	elif not data.get('is_video'):
		image_url = data.get('url')
		image = image_pattern.search(image_url)

		filename = image.group('filename')
		filetype = image.group('filetype')
		return download(image_url, filename, filetype)
	else:
		print('Could not download post.')
		

def download(link, filename, filetype = 'mp4'):
	r = requests.get(link, headers=user_agent)
	
	with open(f'{filename}.{filetype}', 'wb') as f:
		f.write(r.content)

def combine(video, audio):
	subprocess.call(f'ffmpeg -i {video}.mp4 -i {audio}.mp4 -c:v copy -c:a aac {video[0:-1]}.mp4', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) # combine video and audio with FFMPEG
	os.remove(video + '.mp4')
	os.remove(audio + '.mp4')

if __name__ == '__main__':
	url = input('Enter Reddit URL: ') + '.json'
	main(url)