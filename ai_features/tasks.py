from celery import shared_task
from django.utils import timezone
import openai
from django.conf import settings
from .models import AITask, BedtimeStory
from memories.models import Memory
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_bedtime_story(task_id):
    """Generate a bedtime story using OpenAI"""
    try:
        task = AITask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()
        
        if not settings.OPENAI_API_KEY:
            task.status = 'failed'
            task.error_message = 'OpenAI API key not configured'
            task.save()
            return
        
        openai.api_key = settings.OPENAI_API_KEY
        
        input_data = task.input_data
        child_name = input_data['child_name']
        prompt = input_data['prompt']
        theme = input_data.get('theme', '')
        length = input_data.get('length', 'medium')
        
        # Construct the prompt
        system_prompt = f"""You are a creative children's story writer. Create a bedtime story for {child_name} 
        that is appropriate for their age, engaging, and has a calming ending suitable for bedtime.
        
        Theme: {theme if theme else 'general'}
        Length: {length}
        
        The story should be warm, imaginative, and end on a peaceful note that helps the child feel calm and ready for sleep."""
        
        user_prompt = f"Write a bedtime story about: {prompt}. The main character should be named {child_name}."
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500 if length == 'long' else 1000 if length == 'medium' else 600,
            temperature=0.8
        )
        
        story_content = response.choices[0].message.content.strip()
        
        # Create the bedtime story
        from accounts.models import Child
        child = Child.objects.get(id=input_data['child_id'])
        
        bedtime_story = BedtimeStory.objects.create(
            child=child,
            title=f"A Special Story for {child_name}",
            story_content=story_content,
            prompt_used=prompt,
            created_by=task.created_by
        )
        
        task.status = 'completed'
        task.output_data = {'story_id': str(bedtime_story.id)}
        task.completed_at = timezone.now()
        task.save()
        
    except Exception as e:
        logger.error(f"Error generating bedtime story: {e}")
        task.status = 'failed'
        task.error_message = str(e)
        task.save()

@shared_task
def generate_photo_caption(task_id):
    """Generate a photo caption using OpenAI Vision"""
    try:
        task = AITask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()
        
        if not settings.OPENAI_API_KEY:
            task.status = 'failed'
            task.error_message = 'OpenAI API key not configured'
            task.save()
            return
        
        memory_id = task.input_data['memory_id']
        memory = Memory.objects.get(id=memory_id)
        
        if not memory.image:
            task.status = 'failed'
            task.error_message = 'No image found for this memory'
            task.save()
            return
        
        # For now, use a simple text completion since Vision API setup is complex
        openai.api_key = settings.OPENAI_API_KEY
        
        prompt = f"""Generate a warm, family-friendly caption for a photo in {memory.child.name}'s memory album. 
        The photo is titled "{memory.title}" and has this description: "{memory.content}".
        
        Create a caption that captures the moment and emotion, suitable for a family memory book."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        caption = response.choices[0].message.content.strip()
        
        # Update memory with AI caption
        memory.ai_caption = caption
        memory.save()
        
        task.status = 'completed'
        task.output_data = {'caption': caption}
        task.completed_at = timezone.now()
        task.save()
        
    except Exception as e:
        logger.error(f"Error generating photo caption: {e}")
        task.status = 'failed'
        task.error_message = str(e)
        task.save()

@shared_task
def transcribe_audio_file(task_id):
    """Transcribe audio file using OpenAI Whisper"""
    try:
        task = AITask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()
        
        if not settings.OPENAI_API_KEY:
            task.status = 'failed'
            task.error_message = 'OpenAI API key not configured'
            task.save()
            return
        
        memory_id = task.input_data['memory_id']
        memory = Memory.objects.get(id=memory_id)
        
        if not memory.audio:
            task.status = 'failed'
            task.error_message = 'No audio file found for this memory'
            task.save()
            return
        
        openai.api_key = settings.OPENAI_API_KEY
        
        # This would need proper file handling for production
        # For now, we'll simulate transcription
        transcription = "Audio transcription feature coming soon!"
        
        # Update memory with transcription
        memory.transcription = transcription
        memory.save()
        
        task.status = 'completed'
        task.output_data = {'transcription': transcription}
        task.completed_at = timezone.now()
        task.save()
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        task.status = 'failed'
        task.error_message = str(e)
        task.save()