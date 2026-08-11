import uuid
from auth import get_supabase_client

def save_to_library(user_id, voice_type, text_input, audio_bytes):
    supabase = get_supabase_client()
    path = f"{user_id}/{uuid.uuid4()}.wav"
    supabase.storage.from_("voice-files").upload(path, audio_bytes, {"content-type": "audio/wav"})
    public_url = supabase.storage.from_("voice-files").get_public_url(path)
    supabase.table("voice_library").insert({
        "user_id": user_id,
        "type": voice_type,
        "text_input": text_input,
        "audio_url": public_url,
        "storage_path": path
    }).execute()

def get_library(user_id, voice_type):
    supabase = get_supabase_client()
    result = (
        supabase.table("voice_library")
        .select("*")
        .eq("user_id", user_id)
        .eq("type", voice_type)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data

def delete_from_library(entry_id, storage_path):
    supabase = get_supabase_client()
    supabase.storage.from_("voice-files").remove([storage_path])
    supabase.table("voice_library").delete().eq("id", entry_id).execute()