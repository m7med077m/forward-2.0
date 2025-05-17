from pyrogram import Client
import asyncio
import logging
import sys
import os
import json
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    FloodWait,
    UserNotParticipant,
    ChatAdminRequired,
    ChannelPrivate,
    SessionRevoked,
    AuthKeyUnregistered
)

# Configure logging
logging.basicConfig(
    format='%(message)s',  # Simplified format
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_copier.log')  # Only log to file, not console
    ]
)
logger = logging.getLogger(__name__)

# Suppress Pyrogram's logging
logging.getLogger('pyrogram').setLevel(logging.WARNING)
logging.getLogger('pyrogram.client').setLevel(logging.WARNING)
logging.getLogger('pyrogram.session').setLevel(logging.WARNING)
logging.getLogger('pyrogram.connection').setLevel(logging.WARNING)

class TelegramCopier:
    def __init__(self):
        self.api_id = 17058698
        self.api_hash = "088f8d5bf0b4b5c0536b039bb6bdf1d2"
        self.bot_token = "6253336643:AAG_uJJpXnvgPkrhAAHleCPA0xUZ6-8L9Ok"  # Your bot token
        self.bot_chat_id = "933493534"  # Your chat ID
        self.app = None
        self.bot = None
        self.session_file = "session.json"
        self.session_name = "my_account"  # Changed from hardcoded to instance variable

    def save_session(self, session_string):
        """Save session string to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump({'session_string': session_string}, f)
            print("✓ Session saved successfully")
            logger.info("Session saved successfully")
        except Exception as e:
            print(f"❌ Error saving session: {e}")
            logger.error(f"Error saving session: {e}")

    def load_session(self):
        """Load session string from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    data = json.load(f)
                    return data.get('session_string')
            return None
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            logger.error(f"Error loading session: {e}")
            return None

    def delete_session(self):
        """Delete the session file and session directory"""
        try:
            # Delete session file
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print("✓ Session file deleted")
            
            # Delete session directory
            session_dir = f"{self.session_name}.session"
            if os.path.exists(session_dir):
                os.remove(session_dir)
                print("✓ Session directory deleted")
            
            logger.info("Session files deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            logger.error(f"Error deleting session: {e}")

    async def send_monitor_message(self, message):
        """Send monitoring message using the bot"""
        try:
            if not self.bot:
                # Initialize bot if not already done
                self.bot = Client(
                    "my_bot",
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    bot_token=self.bot_token,
                    in_memory=True
                )
                await self.bot.start()
            
            # Convert chat_id to integer
            chat_id = int(self.bot_chat_id)
            
            # Send message using bot
            sent_message = await self.bot.send_message(chat_id, message)
            print(f"Debug: Notification sent via bot to {chat_id}")
            return sent_message
        except Exception as e:
            print(f"Error sending notification: {e}")
            logger.error(f"Error sending notification: {e}")
            return None

    async def start(self):
        """Start the application"""
        try:
            print("\n=== Session Management ===")
            print("1. Use existing session (if available)")
            print("2. Enter session string manually")
            print("3. Create new session")
            
            while True:
                try:
                    choice = input("\nChoose an option (1-3): ").strip()
                    if choice not in ["1", "2", "3"]:
                        print("Invalid choice. Please enter 1, 2, or 3.")
                        continue
                    break
                except KeyboardInterrupt:
                    print("\nOperation cancelled by user")
                    return False
            
            # Initialize bot first
            try:
                self.bot = Client(
                    "my_bot",
                    api_id=self.api_id,
                    api_hash=self.api_hash,
                    bot_token=self.bot_token,
                    in_memory=True
                )
                await self.bot.start()
                print("✓ Bot initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing bot: {e}")
                logger.error(f"Error initializing bot: {e}")
                return False

            if choice == "1":
                # Try to load existing session
                session_string = self.load_session()
                if session_string:
                    try:
                        # Delete any existing session files first
                        self.delete_session()
                        
                        # Start user client with existing session
                        self.app = Client(
                            self.session_name,
                            api_id=self.api_id,
                            api_hash=self.api_hash,
                            session_string=session_string,
                            in_memory=True  # Use in-memory session
                        )
                        await self.app.start()
                        
                        # Verify account access
                        me = await self.app.get_me()
                        print(f"\n✓ Successfully logged in as: {me.first_name} (@{me.username})")
                        print(f"✓ User ID: {me.id}")
                        logger.info(f"Logged in with existing session as: {me.first_name} (@{me.username})")
                        
                        return True
                    except (SessionRevoked, AuthKeyUnregistered) as e:
                        print("\n❌ Session has been revoked or invalidated.")
                        print("This usually happens when you terminate all sessions in Telegram.")
                        print("Please create a new session.")
                        self.delete_session()
                        choice = "3"
                    except Exception as e:
                        print(f"❌ Error using existing session: {e}")
                        logger.error(f"Error using existing session: {e}")
                        print("Will create a new session...")
                        choice = "3"
                else:
                    print("No existing session found. Creating new session...")
                    choice = "3"
            
            if choice == "2":
                # Manual session string input
                while True:
                    try:
                        session_string = input("\nEnter your session string: ").strip()
                        if not session_string:
                            print("Session string cannot be empty. Please try again or press Ctrl+C to create new session.")
                            continue
                        break
                    except KeyboardInterrupt:
                        print("\nSwitching to new session creation...")
                        choice = "3"
                        break
                
                if choice == "2":
                    try:
                        # Delete any existing session files first
                        self.delete_session()
                        
                        # Start user client with provided session
                        self.app = Client(
                            self.session_name,
                            api_id=self.api_id,
                            api_hash=self.api_hash,
                            session_string=session_string,
                            in_memory=True  # Use in-memory session
                        )
                        await self.app.start()
                        
                        # Verify account access
                        me = await self.app.get_me()
                        print(f"\n✓ Successfully logged in as: {me.first_name} (@{me.username})")
                        print(f"✓ User ID: {me.id}")
                        logger.info(f"Logged in with manual session as: {me.first_name} (@{me.username})")
                        
                        # Save the working session
                        self.save_session(session_string)
                        
                        return True
                    except (SessionRevoked, AuthKeyUnregistered) as e:
                        print("\n❌ Session has been revoked or invalidated.")
                        print("This usually happens when you terminate all sessions in Telegram.")
                        print("Please create a new session.")
                        choice = "3"
                    except Exception as e:
                        print(f"❌ Error using provided session: {e}")
                        logger.error(f"Error using provided session: {e}")
                        print("Will create a new session...")
                        choice = "3"
            
            if choice == "3":
                # Create new session
                print("\nCreating new session...")
                try:
                    # Delete any existing session files first
                    self.delete_session()
                    
                    # Create new client with in-memory session
                    self.app = Client(
                        self.session_name,
                        api_id=self.api_id,
                        api_hash=self.api_hash,
                        in_memory=True  # Use in-memory session
                    )
                    await self.app.start()
                    
                    # Get session string
                    session_string = await self.app.export_session_string()
                    self.save_session(session_string)
                    
                    # Verify account access
                    me = await self.app.get_me()
                    print(f"\n✓ Successfully logged in as: {me.first_name} (@{me.username})")
                    print(f"✓ User ID: {me.id}")
                    logger.info(f"Created new session for: {me.first_name} (@{me.username})")
                    
                    return True
                except Exception as e:
                    print(f"❌ Error creating new session: {e}")
                    logger.error(f"Error creating new session: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            logger.error(f"Error starting application: {e}")
            return False

    async def verify_channel_access(self, channel_id):
        """Verify access to a channel"""
        try:
            print(f"\nVerifying channel: {channel_id}")
            
            # Try to get chat info
            try:
                chat = await self.app.get_chat(channel_id)
            except ChannelPrivate:
                print("\n❌ This is a private channel.")
                print("Please make sure:")
                print("1. You are a member of this channel")
                print("2. You have joined the channel before trying to access it")
                print("3. The channel link is correct")
                return None
            except Exception as e:
                print(f"\n❌ Error accessing channel: {e}")
                print("Please check if the channel ID/link is correct")
                return None
            
            # Get channel info
            print("\n=== Channel Information ===")
            print(f"✓ Name: {chat.title}")
            print(f"✓ ID: {chat.id}")
            print(f"✓ Type: {chat.type}")
            logger.info(f"Verified channel: {chat.title} (ID: {chat.id})")
            
            # Try to get member count
            try:
                member_count = await self.app.get_chat_members_count(chat.id)
                print(f"✓ Member count: {member_count}")
            except Exception as e:
                print(f"! Could not get member count: {str(e)}")
                logger.warning(f"Could not get member count for {chat.title}: {e}")
            
            # Try to get recent messages
            try:
                messages = await self.app.get_chat_history(chat.id, limit=1)
                async for msg in messages:
                    print(f"✓ Latest message ID: {msg.id}")
                    print(f"✓ Latest message date: {msg.date}")
                    break
            except Exception as e:
                print(f"! Could not get message history: {str(e)}")
                print("This might be because:")
                print("1. You don't have access to message history")
                print("2. The channel is private and you need to join first")
                logger.warning(f"Could not get message history for {chat.title}: {e}")
            
            # Verify permissions
            try:
                me = await self.app.get_me()
                member = await self.app.get_chat_member(chat.id, me.id)
                print(f"\n=== Your Permissions ===")
                print(f"✓ Role: {member.status}")
                if hasattr(member, 'privileges'):
                    print(f"✓ Can post messages: {member.privileges.can_post_messages}")
                    print(f"✓ Can edit messages: {member.privileges.can_edit_messages}")
                else:
                    print("! Could not get detailed permissions")
                logger.info(f"User permissions in {chat.title}: {member.status}")
            except UserNotParticipant:
                print("\n❌ You are not a member of this channel.")
                print("Please join the channel first before trying to access it.")
                return None
            except Exception as e:
                print(f"! Could not verify permissions: {str(e)}")
                logger.warning(f"Could not verify permissions in {chat.title}: {e}")
            
            return chat
            
        except Exception as e:
            print(f"\n❌ Error accessing channel: {e}")
            print("Please make sure:")
            print("1. The channel ID/link is correct")
            print("2. You are a member of the channel")
            print("3. You have the necessary permissions")
            logger.error(f"Error accessing channel {channel_id}: {e}")
            return None

    async def download_large_video(self, message, progress_callback=None):
        """Download video files with progress tracking"""
        try:
            if not message or not message.video:
                raise Exception("Invalid video message")

            # Get file size
            file_size = message.video.file_size
            print(f"\n📊 Video Information:")
            print(f"✓ File size: {file_size / (1024*1024):.2f} MB")
            print(f"✓ Duration: {message.video.duration} seconds")
            print(f"✓ Resolution: {message.video.width}x{message.video.height}")
            
            # Create temporary directory if it doesn't exist
            temp_dir = "temp_downloads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Generate unique filename
            temp_file = os.path.join(temp_dir, f"temp_video_{message.id}.mp4")
            
            try:
                # Download the media with progress callback
                downloaded_file = await self.app.download_media(
                    message,
                    file_name=temp_file,
                    progress=progress_callback
                )
                
                if downloaded_file:
                    print(f"✓ Video downloaded successfully to: {downloaded_file}")
                    return downloaded_file
                else:
                    raise Exception("Download failed - no file returned")
                
            except Exception as e:
                print(f"❌ Error during video download: {e}")
                # Clean up partial download
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise
                
        except Exception as e:
            print(f"❌ Error in download_large_video: {e}")
            raise

    async def download_progress(self, current, total, progress_msg_id=None):
        """Callback for download progress"""
        try:
            percentage = current * 100 / total
            bar_length = 30
            filled_length = int(bar_length * current // total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            progress_text = f'\r⬇️ Downloading: [{bar}] {percentage:.1f}%'
            print(progress_text, end='')
            
            # Update progress message every 5%
            if int(percentage) % 5 == 0 and percentage > 0:
                progress_msg = (
                    f"📥 Download Progress:\n"
                    f"[{bar}] {percentage:.1f}%\n"
                    f"Size: {current/(1024*1024):.1f}MB / {total/(1024*1024):.1f}MB"
                )
                if progress_msg_id:
                    try:
                        await self.bot.edit_message_text(
                            chat_id=int(self.bot_chat_id),
                            message_id=progress_msg_id,
                            text=progress_msg
                        )
                    except Exception as e:
                        print(f"Could not update progress message: {e}")
                else:
                    # Send initial progress message
                    msg = await self.send_monitor_message(progress_msg)
                    return msg.id
            
            if current == total:
                print()  # New line when complete
                # Update completion message
                completion_msg = (
                    f"✅ Download Complete!\n"
                    f"Total size: {total/(1024*1024):.1f}MB"
                )
                if progress_msg_id:
                    try:
                        await self.bot.edit_message_text(
                            chat_id=int(self.bot_chat_id),
                            message_id=progress_msg_id,
                            text=completion_msg
                        )
                    except Exception as e:
                        print(f"Could not update completion message: {e}")
                return None
                
        except Exception as e:
            print(f"\nError in progress callback: {e}")
            await self.send_monitor_message(f"⚠️ Error in progress tracking: {e}")
            return None

    async def edit_message_with_retry(self, chat_id, message_id, text, max_retries=3):
        """Edit message with retry mechanism for rate limits"""
        for attempt in range(max_retries):
            try:
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text
                )
                return True
            except FloodWait as e:
                wait_time = e.value
                print(f"Rate limit hit. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"Failed to edit message after {max_retries} attempts: {e}")
                    return False
                await asyncio.sleep(2)  # Wait 2 seconds before retry
        return False

    async def copy_messages(self, source, target, start_id=0, end_id=0):
        """Copy messages from source to target channel by downloading and re-uploading"""
        try:
            # Get messages
            print("\n📥 Fetching messages...")
            status_msg = await self.send_monitor_message("🔄 Starting message fetch...")
            status_msg_id = status_msg.id if status_msg else None
            
            # Add delay between message edits
            last_edit_time = 0
            min_edit_interval = 2  # Minimum seconds between edits
            
            # Network speed tracking
            speed_samples = []
            max_samples = 10  # Keep last 10 speed samples
            
            # Fetch all messages first
            messages = []
            try:
                async for message in self.app.get_chat_history(source):
                    if start_id != 0 and message.id < start_id:
                        continue
                    if end_id != 0 and message.id > end_id:
                        continue
                    messages.append(message)
            except Exception as e:
                error_msg = f"❌ Error fetching messages: {e}"
                print(error_msg)
                if status_msg_id:
                    await self.edit_message_with_retry(
                        int(self.bot_chat_id),
                        status_msg_id,
                        error_msg
                    )
                return
            
            # Sort messages by ID to ensure correct order
            messages.sort(key=lambda x: x.id)
            
            total = len(messages)
            if total == 0:
                no_msg = "❌ No messages found in the specified range"
                print(no_msg)
                if status_msg_id:
                    await self.edit_message_with_retry(
                        int(self.bot_chat_id),
                        status_msg_id,
                        no_msg
                    )
                return
                
            start_msg = f"📥 Found {total} messages to copy"
            print(start_msg)
            if status_msg_id:
                await self.edit_message_with_retry(
                    int(self.bot_chat_id),
                    status_msg_id,
                    start_msg
                )
            
            # Copy messages
            success = 0
            failed = 0
            start_time = asyncio.get_event_loop().time()
            last_download_time = start_time
            last_download_bytes = 0
            last_upload_time = start_time
            last_upload_bytes = 0
            
            # Create temporary directory for downloads
            temp_dir = "temp_downloads"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            for i, msg in enumerate(messages, 1):
                try:
                    # Add delay between messages to prevent rate limiting
                    if i > 1:
                        await asyncio.sleep(1)  # Reduced delay to 1 second
                    
                    print(f"\n📝 Processing message {msg.id} ({i}/{total})...")
                    
                    # Get message details
                    message_details = []
                    if msg.media:
                        media_type = msg.media.value
                        message_details.append(f"📎 Type: {media_type}")
                        
                        if msg.video:
                            message_details.append(f"🎥 Video: {msg.video.file_size / (1024*1024):.1f}MB")
                            message_details.append(f"⏱️ Duration: {msg.video.duration}s")
                            message_details.append(f"📐 Resolution: {msg.video.width}x{msg.video.height}")
                        elif msg.document:
                            message_details.append(f"📄 Document: {msg.document.file_name}")
                            message_details.append(f"📦 Size: {msg.document.file_size / (1024*1024):.1f}MB")
                        elif msg.photo:
                            message_details.append(f"🖼️ Photo: {msg.photo[-1].file_size / (1024*1024):.1f}MB")
                        elif msg.audio:
                            message_details.append(f"🎵 Audio: {msg.audio.file_size / (1024*1024):.1f}MB")
                            message_details.append(f"⏱️ Duration: {msg.audio.duration}s")
                    
                    if msg.caption:
                        caption_preview = msg.caption[:50] + "..." if len(msg.caption) > 50 else msg.caption
                        message_details.append(f"📝 Caption: {caption_preview}")
                    
                    # Update status message with detailed information
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_edit_time >= min_edit_interval:
                        status_text = (
                            f"📝 Processing message {msg.id} ({i}/{total})...\n"
                            f"📅 Date: {msg.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            + "\n".join(message_details) + "\n"
                            f"✓ Success: {success}\n"
                            f"❌ Failed: {failed}"
                        )
                        if status_msg_id:
                            if await self.edit_message_with_retry(
                                int(self.bot_chat_id),
                                status_msg_id,
                                status_text
                            ):
                                last_edit_time = current_time
                    
                    # Handle media messages
                    if msg.media:
                        try:
                            # Get media type
                            media_type = msg.media.value
                            if media_type == "web_page":
                                print("⚠️ Skipping web page")
                                continue
                                
                            print(f"🎥 Processing {media_type}...")
                            
                            # Download media with progress tracking
                            async def progress_callback(current, total):
                                try:
                                    nonlocal last_download_time, last_download_bytes, last_edit_time, speed_samples
                                    current_time = asyncio.get_event_loop().time()
                                    time_diff = current_time - last_download_time
                                    
                                    if time_diff >= 1.0:  # Update speed every second
                                        bytes_diff = current - last_download_bytes
                                        download_speed = bytes_diff / time_diff  # bytes per second
                                        download_speed_mb = download_speed / (1024 * 1024)  # MB/s
                                        
                                        # Update speed samples
                                        speed_samples.append(download_speed_mb)
                                        if len(speed_samples) > max_samples:
                                            speed_samples.pop(0)
                                        
                                        # Calculate average speed
                                        avg_speed = sum(speed_samples) / len(speed_samples)
                                        
                                        last_download_time = current_time
                                        last_download_bytes = current
                                        
                                        # Only update message if enough time has passed
                                        if current_time - last_edit_time >= min_edit_interval:
                                            percentage = current * 100 / total
                                            bar_length = 30
                                            filled_length = int(bar_length * current // total)
                                            bar = '█' * filled_length + '░' * (bar_length - filled_length)
                                            
                                            # Update status message with download progress
                                            download_status = (
                                                f"📝 Processing message {msg.id} ({i}/{total})...\n"
                                                f"📅 Date: {msg.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                                + "\n".join(message_details) + "\n"
                                                f"📥 Download Progress:\n"
                                                f"[{bar}] {percentage:.1f}%\n"
                                                f"Size: {current/(1024*1024):.1f}MB / {total/(1024*1024):.1f}MB\n"
                                                f"⬇️ Current Speed: {download_speed_mb:.1f} MB/s\n"
                                                f"⬇️ Average Speed: {avg_speed:.1f} MB/s\n"
                                                f"✓ Success: {success}\n"
                                                f"❌ Failed: {failed}"
                                            )
                                            if status_msg_id:
                                                if await self.edit_message_with_retry(
                                                    int(self.bot_chat_id),
                                                    status_msg_id,
                                                    download_status
                                                ):
                                                    last_edit_time = current_time
                                except Exception as e:
                                    print(f"Error in progress callback: {e}")
                            
                            # Generate unique filename for this message
                            temp_file = os.path.join(temp_dir, f"temp_{msg.id}_{media_type}.tmp")
                            
                            # Download the media
                            media = await self.app.download_media(
                                msg,
                                file_name=temp_file,
                                progress=progress_callback
                            )
                            
                            if not media:
                                raise Exception("Download failed - no file returned")
                            
                            # Prepare caption
                            caption = msg.caption if msg.caption else ""
                            
                            # Send media using appropriate handler
                            media_handlers = {
                                "photo": self.app.send_photo,
                                "video": self.app.send_video,
                                "document": self.app.send_document,
                                "audio": self.app.send_audio,
                                "voice": self.app.send_voice,
                                "animation": self.app.send_animation,
                                "sticker": self.app.send_sticker,
                                "video_note": self.app.send_video_note
                            }
                            
                            handler = media_handlers.get(media_type)
                            if handler:
                                # Track upload progress
                                upload_start_time = asyncio.get_event_loop().time()
                                upload_start_bytes = 0
                                upload_speed_samples = []
                                
                                async def upload_progress(current, total):
                                    try:
                                        nonlocal last_upload_time, last_upload_bytes, last_edit_time, upload_speed_samples
                                        current_time = asyncio.get_event_loop().time()
                                        time_diff = current_time - last_upload_time
                                        
                                        if time_diff >= 1.0:  # Update speed every second
                                            bytes_diff = current - last_upload_bytes
                                            upload_speed = bytes_diff / time_diff  # bytes per second
                                            upload_speed_mb = upload_speed / (1024 * 1024)  # MB/s
                                            
                                            # Update speed samples
                                            upload_speed_samples.append(upload_speed_mb)
                                            if len(upload_speed_samples) > max_samples:
                                                upload_speed_samples.pop(0)
                                            
                                            # Calculate average speed
                                            avg_upload_speed = sum(upload_speed_samples) / len(upload_speed_samples)
                                            
                                            last_upload_time = current_time
                                            last_upload_bytes = current
                                            
                                            # Only update message if enough time has passed
                                            if current_time - last_edit_time >= min_edit_interval:
                                                percentage = current * 100 / total
                                                bar_length = 30
                                                filled_length = int(bar_length * current // total)
                                                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                                                
                                                # Update status message with upload progress
                                                upload_status = (
                                                    f"📝 Processing message {msg.id} ({i}/{total})...\n"
                                                    f"📅 Date: {msg.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                                    + "\n".join(message_details) + "\n"
                                                    f"📤 Upload Progress:\n"
                                                    f"[{bar}] {percentage:.1f}%\n"
                                                    f"Size: {current/(1024*1024):.1f}MB / {total/(1024*1024):.1f}MB\n"
                                                    f"⬆️ Current Speed: {upload_speed_mb:.1f} MB/s\n"
                                                    f"⬆️ Average Speed: {avg_upload_speed:.1f} MB/s\n"
                                                    f"✓ Success: {success}\n"
                                                    f"❌ Failed: {failed}"
                                                )
                                                if status_msg_id:
                                                    if await self.edit_message_with_retry(
                                                        int(self.bot_chat_id),
                                                        status_msg_id,
                                                        upload_status
                                                    ):
                                                        last_edit_time = current_time
                                    except Exception as e:
                                        print(f"Error in upload progress callback: {e}")
                                
                                # Send media with appropriate parameters
                                if media_type == "video":
                                    await handler(
                                        target,
                                        media,
                                        caption=caption,
                                        duration=msg.video.duration if hasattr(msg, 'video') else None,
                                        width=msg.video.width if hasattr(msg, 'video') else None,
                                        height=msg.video.height if hasattr(msg, 'video') else None,
                                        progress=upload_progress
                                    )
                                elif media_type == "photo":
                                    await handler(
                                        target,
                                        media,
                                        caption=caption,
                                        has_spoiler=msg.has_media_spoiler if hasattr(msg, 'has_media_spoiler') else False,
                                        progress=upload_progress
                                    )
                                elif media_type == "document":
                                    await handler(
                                        target,
                                        media,
                                        caption=caption,
                                        file_name=msg.document.file_name if hasattr(msg, 'document') else None,
                                        progress=upload_progress
                                    )
                                else:
                                    await handler(target, media, caption=caption, progress=upload_progress)
                                    
                                print(f"✓ Sent {media_type}")
                            else:
                                print(f"⚠️ No handler for media type: {media_type}")
                            
                        except Exception as e:
                            print(f"⚠️ Could not process media: {e}")
                            failed += 1
                            continue
                            
                    # Handle text messages
                    elif msg.text:
                        try:
                            await self.app.send_message(target, msg.text)
                            print("✓ Sent text message")
                            success += 1
                        except Exception as e:
                            print(f"⚠️ Could not send text message: {e}")
                            failed += 1
                            continue
                    
                    success += 1
                    
                    # Update progress message
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_edit_time >= min_edit_interval:
                        elapsed_time = current_time - start_time
                        speed = i / elapsed_time if elapsed_time > 0 else 0
                        remaining = (total - i) / speed if speed > 0 else 0
                        
                        status = (
                            f"📊 Progress: {i}/{total} messages\n"
                            f"✓ Success: {success}\n"
                            f"❌ Failed: {failed}\n"
                            f"⚡ Speed: {speed:.1f} msg/sec\n"
                            f"⏳ Remaining: {remaining:.0f} seconds"
                        )
                        if status_msg_id:
                            if await self.edit_message_with_retry(
                                int(self.bot_chat_id),
                                status_msg_id,
                                status
                            ):
                                last_edit_time = current_time
                        
                except FloodWait as e:
                    wait_time = e.value
                    wait_msg = f"⏳ Rate limit hit. Waiting {wait_time} seconds..."
                    print(wait_msg)
                    if status_msg_id:
                        await self.edit_message_with_retry(
                            int(self.bot_chat_id),
                            status_msg_id,
                            wait_msg
                        )
                    await asyncio.sleep(wait_time)
                    continue
                except Exception as e:
                    failed += 1
                    error_msg = f"❌ Error copying message {msg.id}: {e}"
                    print(error_msg)
                    if status_msg_id:
                        await self.edit_message_with_retry(
                            int(self.bot_chat_id),
                            status_msg_id,
                            error_msg
                        )
                finally:
                    # Clean up downloaded media
                    if 'media' in locals() and media and os.path.exists(media):
                        try:
                            os.remove(media)
                        except Exception as e:
                            print(f"⚠️ Could not delete temporary file: {e}")
            
            # Calculate final statistics
            total_time = asyncio.get_event_loop().time() - start_time
            avg_speed = total / total_time if total_time > 0 else 0
            
            # Send completion message
            final_status = (
                f"✅ Copy completed!\n\n"
                f"📊 Final Statistics:\n"
                f"✓ Total messages: {total}\n"
                f"✓ Successfully copied: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏱️ Total time: {total_time:.0f} seconds\n"
                f"⚡ Average speed: {avg_speed:.1f} msg/sec"
            )
            if status_msg_id:
                await self.edit_message_with_retry(
                    int(self.bot_chat_id),
                    status_msg_id,
                    final_status
                )
            
        except Exception as e:
            error_msg = f"❌ Fatal error: {str(e)}"
            print(error_msg)
            if status_msg_id:
                await self.edit_message_with_retry(
                    int(self.bot_chat_id),
                    status_msg_id,
                    error_msg
                )

    async def stop(self):
        """Stop the application"""
        try:
            if self.app:
                await self.app.stop()
            if self.bot:
                await self.bot.stop()
            print("\n✓ Application stopped successfully")
        except Exception as e:
            print(f"\n❌ Error stopping application: {e}")

async def main():
    print("\n=== Telegram Message Copier ===")
    print("Simple tool to copy messages between channels")
    logger.info("Starting Telegram Message Copier")
    
    # Initialize copier
    copier = TelegramCopier()
    if not await copier.start():
        print("Failed to start the application")
        logger.error("Failed to start the application")
        return
    
    try:
        # Get and verify source channel
        while True:
            source = input("\nEnter source channel (ID/username/link): ").strip()
            if not source:
                print("Source channel cannot be empty")
                continue
                
            print("\n=== Verifying Source Channel ===")
            source_chat = await copier.verify_channel_access(source)
            if not source_chat:
                print("❌ Could not access source channel. Please try again.")
                continue
            
            confirm_source = input("\nIs this the correct source channel? (y/n): ").strip().lower()
            if confirm_source == 'y':
                break
            print("Please enter the source channel again.")
        
        # Get and verify target channel
        while True:
            target = input("\nEnter target channel (ID/username/link): ").strip()
            if not target:
                print("Target channel cannot be empty")
                continue
                
            print("\n=== Verifying Target Channel ===")
            target_chat = await copier.verify_channel_access(target)
            if not target_chat:
                print("❌ Could not access target channel. Please try again.")
                continue
            
            confirm_target = input("\nIs this the correct target channel? (y/n): ").strip().lower()
            if confirm_target == 'y':
                break
            print("Please enter the target channel again.")
        
        # Get message range
        while True:
            try:
                start_id = int(input("\nEnter start message ID (0 for beginning): ").strip() or "0")
                end_id = int(input("Enter end message ID (0 for latest): ").strip() or "0")
                if start_id < 0 or end_id < 0:
                    print("Message IDs cannot be negative")
                    continue
                if end_id != 0 and start_id > end_id:
                    print("Start ID cannot be greater than End ID")
                    continue
                break
            except ValueError:
                print("Invalid message ID. Please enter numbers only.")
        
        # Final confirmation
        print("\n=== Final Confirmation ===")
        print(f"Source Channel: {source_chat.title} (ID: {source_chat.id})")
        print(f"Target Channel: {target_chat.title} (ID: {target_chat.id})")
        print(f"Message Range: {start_id} to {end_id}")
        print("\nWARNING: This will copy messages from the source channel to the target channel.")
        print("Make sure you have the necessary permissions in both channels.")
        
        confirm = input("\nDo you want to proceed with copying? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Copy operation cancelled by user.")
            logger.info("Copy operation cancelled by user")
            await copier.stop()
            return
        
        # Start copying
        print("\nStarting copy process...")
        await copier.copy_messages(source_chat.id, target_chat.id, start_id, end_id)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        logger.info("Operation cancelled by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        logger.error(f"An error occurred: {e}")
    finally:
        await copier.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        logger.info("Program terminated by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
