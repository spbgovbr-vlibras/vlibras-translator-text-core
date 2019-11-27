import errno
import logging
import os
import shutil
import subprocess

import ffmpeg
import pyvirtualdisplay

from util import configreader


class RenderingError(Exception):
    """
    Raised when any LIBRAS video rendering step fails
    """
    pass


class PlayerWrapper:

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__playercfg = configreader.load_configs("LibrasPlayer")
        self.__ffmpegcfg = configreader.load_configs("FFmpeg")
        self.__temp_dir = self.__playercfg.get("TempDir", "/tmp")

    def __handle_input_data(
        self,
        iput_data: str,
        correlation_tag: str
    ) -> str:

        gloss_name = "{}.{}".format(correlation_tag, "txt")
        gloss_path = os.path.join(self.__temp_dir, correlation_tag, gloss_name)
        os.makedirs(os.path.dirname(gloss_path), exist_ok=True)

        self.__logger.debug("Writing input file.")
        with open(gloss_path, "w") as gfile:
            gfile.write("0#{}".format(iput_data))

        self.__logger.debug("{} successfully created.".format(gloss_path))

        return gloss_path

    def __start_frames_capture(
        self,
        input_file: str,
        correlation_tag: str,
        player_params: dict
    ) -> str:

        frames_dir = os.path.join(self.__temp_dir, correlation_tag, "frames")
        frames_path = os.path.join(frames_dir, "img_*.jpg")

        display_width = self.__playercfg.get("DisplayWidth", "1024")
        display_height = self.__playercfg.get("DisplayHeight", "768")

        unity_cmd = [
            self.__playercfg.get("PlayerBin", "None"),
            "--id", correlation_tag,
            "--glosapath", input_file,
            "--videopath", frames_dir,
            "--width", display_width,
            "--height", display_height,
            "--speed", self.__playercfg.get("AnimationSpeed", "70"),
            "--framerate", self.__playercfg.get("VideoFramerate", "24"),
            "--avatar", self.__playercfg.get("Avatar", "icaro"),
            "--subtitle", self.__playercfg.get("Caption", "off"),
            "--bundlespath", self.__playercfg.get("BundlesPath", "./Bundles")]

        xephyr = pyvirtualdisplay.Display(
            visible=False,
            size=(display_width, display_height))

        self.__logger.debug("Starting virtual display.")
        xephyr.start()

        try:
            if not os.path.exists(frames_dir):
                os.makedirs(frames_dir)

            self.__logger.debug("Generating video frames.")
            subprocess.check_call(unity_cmd, stdout=open(os.devnull, "w"))

            self.__logger.debug(
                "{} successfully generated.".format(frames_path))

        except OSError as ex:
            if ex.errno == errno.ENOENT:
                self.__logger.exception("'{0}' not found.".format(*unity_cmd))
            else:
                self.__logger.exception(
                    "'{0}' spawn failed.".format(*unity_cmd))

        except subprocess.CalledProcessError:
            self.__logger.exception(
                "'{0}' returned a non-zero exit code.".format(*unity_cmd))

        finally:
            xephyr.stop()
            return frames_path

    def __start_video_rendering(
        self,
        frames_path: str,
        correlation_tag: str
    ) -> str:

        video_name = "{}.{}".format(correlation_tag, "mp4")
        video_path = os.path.join(self.__temp_dir, correlation_tag, video_name)

        try:
            self.__logger.debug("Rendering video.")
            (
                ffmpeg
                .input(frames_path, pattern_type="glob", framerate=24)
                .output(video_path, pix_fmt="yuv420p")
                .global_args("-y", "-loglevel", "error")
                .run()
            )

            self.__logger.debug("{} successfully rendered.".format(video_path))

        except ffmpeg.Error:
            self.__logger.exception("FFmpeg returned a non-zero exit code.")

        finally:
            shutil.rmtree(os.path.dirname(frames_path), ignore_errors=True)
            return video_path

    def run(
        self,
        gloss: str,
        correlation_tag: str,
        options: dict = {}
    ) -> tuple:

        gloss_file = self.__handle_input_data(gloss, correlation_tag)
        libras_frames = self.__start_frames_capture(
            gloss_file, correlation_tag, options)
        libras_video = self.__start_video_rendering(
            libras_frames, correlation_tag)

        if not os.path.isfile(libras_video):
            raise RenderingError("Video not rendered.")

        libras_video_size = 0
        try:
            libras_video_size = os.path.getsize(libras_video)
        except:
            self.__logger.warning("Failed to get video size.")
            pass

        libras_video_duration = 0
        try:
            probe = ffmpeg.probe(libras_video)
            streams = (s for s in probe["streams"]
                       if s["codec_type"] == "video")
            duration = next(streams, None).get("duration", 0)
            libras_video_duration = int(float(duration) * 1000)

        except ffmpeg.Error:
            self.__logger.exception("Failed to get video duration.")

        return libras_video, libras_video_size, libras_video_duration
