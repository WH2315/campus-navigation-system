using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

public class VoiceQAController : MonoBehaviour
{
    public event Action<string, string> VoiceAnswerReady;

    [Header("API")]
    [SerializeField] private string apiBaseUrl = "http://127.0.0.1:8000";

    [Header("UI")]
    [SerializeField] private Button startRecordButton;
    [SerializeField] private Button stopAndAskButton;
    [SerializeField] private InputField currentSpotInput;
    [SerializeField] private Text resultText;

    [Header("Record Settings")]
    [SerializeField] private int maxRecordSeconds = 8;
    [SerializeField] private string language = "zh";

    private AudioClip recordedClip;
    private string microphoneName;

    private void Awake()
    {
        microphoneName = Microphone.devices.Length > 0 ? Microphone.devices[0] : null;

        if (startRecordButton != null)
        {
            startRecordButton.onClick.AddListener(StartRecording);
        }

        if (stopAndAskButton != null)
        {
            stopAndAskButton.onClick.AddListener(StopAndAsk);
        }
    }

    private void StartRecording()
    {
        if (string.IsNullOrEmpty(microphoneName))
        {
            SetResult("未检测到麦克风设备。");
            return;
        }

        recordedClip = Microphone.Start(microphoneName, false, Mathf.Max(2, maxRecordSeconds), 16000);
        SetResult("录音中... 点击 StopAndAskButton 发送语音提问。");
    }

    private void StopAndAsk()
    {
        if (string.IsNullOrEmpty(microphoneName))
        {
            SetResult("未检测到麦克风设备。");
            return;
        }

        if (!Microphone.IsRecording(microphoneName))
        {
            SetResult("当前没有正在录音，请先点击开始录音。");
            return;
        }

        int position = Microphone.GetPosition(microphoneName);
        Microphone.End(microphoneName);

        if (recordedClip == null || position <= 0)
        {
            SetResult("录音数据为空，请重试。");
            return;
        }

        float[] samples = new float[position * recordedClip.channels];
        recordedClip.GetData(samples, 0);
        AudioClip clipped = AudioClip.Create("voice_question", position, recordedClip.channels, recordedClip.frequency, false);
        clipped.SetData(samples, 0);

        byte[] wavBytes = WavUtility.FromAudioClip(clipped);
        StartCoroutine(SendVoiceQuestion(wavBytes));
    }

    private IEnumerator SendVoiceQuestion(byte[] wavBytes)
    {
        string url = apiBaseUrl + "/api/v1/session/voice-chat";

        WWWForm form = new WWWForm();
        form.AddField("language", language);
        form.AddField("current_spot_id", currentSpotInput != null ? currentSpotInput.text.Trim() : "");
        form.AddBinaryData("audio", wavBytes, "question.wav", "audio/wav");

        using (UnityWebRequest req = UnityWebRequest.Post(url, form))
        {
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                SetResult("语音问答失败: " + req.error + " | " + req.downloadHandler.text);
                yield break;
            }

            try
            {
                VoiceChatResponse resp = JsonUtility.FromJson<VoiceChatResponse>(req.downloadHandler.text);
                SetResult("识别结果: " + resp.transcript + "\n\n回答: " + resp.answer);
                VoiceAnswerReady?.Invoke(resp.transcript, resp.answer);
            }
            catch (Exception e)
            {
                SetResult("响应解析失败: " + e.Message + " | raw: " + req.downloadHandler.text);
            }
        }
    }

    private void SetResult(string text)
    {
        if (resultText != null)
        {
            resultText.text = text;
        }
    }
}
