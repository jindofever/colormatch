import os
import base64
from PIL import Image
import io


from openai import OpenAI

client = OpenAI()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def submit_image_prompt(image_path):
	content = [
		{
			"type": "text",
			"text": prompt
		}
	]

	for i in image_path:

		base64_image = encode_image(i)

		content.append(
			{
				"type": "image_url",
				"image_url": {
					"url": f"data:image/jpeg;base64,{base64_image}"
				}
			}
		)

	response = client.chat.completions.create(
		model="gpt-4-turbo",
		messages=[
			{
				"role": "system",
				"content": system_prompt
			},
			{
				"role": "user",
				"content": content
			}
		],
		max_tokens=1000
	)

	return response

# trying to get gpt to create pictures for me
# def image_creation(image_path, prompt):
# 	create_images_prompt = "Create images of this person wearing clothes in colors that match their suggested color recommendations and season:" + prompt
# 	response = client.images.edit(
#   		model="dall-e-2",
#   		image=open(image_path[0], "rb"),
# 		prompt=create_images_prompt,
# 		size="1024x1024",
# 		n=1,
# 	)

# 	if response.status_code == 200:
# 		generated_images = response.json()["images"]
# 		# Save or display the generated images
# 		for i, image_data in enumerate(generated_images):
# 			# Decode base64 image data
# 			image_bytes = base64.b64decode(image_data)
# 			# Open the image using PIL
# 			image = Image.open(io.BytesIO(image_bytes))
# 			# Save the image to a file
# 			image.save(f"generated_image_{i+1}.jpg")  # Change the file format if needed
# 			print("image "+i+" saved")
# 	else:
# 		print("Error:", response.text)

system_prompt = """
	You are a Korean color analysis expert tasked with helping clients understand and identify their personal color as one of twelve seasons.

	Please output your response so that it includes the following:
	1. a primary and secondary season
	2. an explanation for why using the steps you followed below
	3. their top 5 color recommendations and color hex based on their seasons.

	The twelve seasons are:
	(1) Bright Spring
	(2) True Spring
	(3) Light Spring
	(4) Light Summer
	(5) True Summer
	(6) Soft Summer
	(7) Soft Autumn
	(8) True Autumn
	(9) Dark Autumn
	(10) Dark Winter
	(11) True Winter
	(12) Bright Winter

	The way you determine a client's season is by looking at only the client's face across the images. Do not look at the background or surroundings at all.

	On their face, you are looking at three characteristics of the client - their eyes, skin, and hair:
	(1) Temperature: Do they appear they Warm or Cool? 
	(2) Value: Do they appear Light or Dark?
	(3) Chroma: Do they appear Bright or Muted?

	For each client, tell them where they sit on the temperature, value, and chroma characteristics.

	To determine their primary and secondary season, follow these steps:
	Step 1. Determine the client's temperature, are they warm or cool?
	Step 2. Determine the client's value, are they light or dark?
	Step 3. Determine the client's chroma, are their features bright or muted?
	Step 4. Of these, determine which of these stands out to you the most - this is their primary characteristic.
	Step 5. Afterwards, if their primary was value or chroma, pick their secondary as the temperature. If it was temperature, their secondary is their chroma.
	Step 6. Follow these formulas to determine which season the client is. The first variable is the primary characteristic and the second variable is the secondary characteristic.
	(1) Bright + Warm = Bright Spring
	(2) Warm + Bright = True Spring
	(3) Light + Warm = Light Spring
	(4) Light + Cool = Light Summer
	(5) Cool + Muted = True Summer
	(6) Muted + Cool = Soft Summer
	(7) Muted + Warm = Soft Autumn
	(8) Warm + Muted = True Autumn
	(9) Dark + Warm = Dark Autumn
	(10) Dark + Cool = Dark Winter
	(11) Cool + Bright = True Winter
	(12) Bright + Cool = Bright Winter
	Step 7. Now repeat step 1 to 6 ten more times, and remember the result that you get each time. Of the ten please output the most common result as their primary season and the second most common result as their secondary season."""

photo_array = ["./mandy1.jpg", "./mandy2.jpg", "./mandy3.jpg"]

prompt = "What is this client's season?"

if __name__ == "__main__":
	response = submit_image_prompt(photo_array)
	new_prompt = response.choices[0].message.content
	print(new_prompt)
	# images = image_creation(photo_array, new_prompt)
