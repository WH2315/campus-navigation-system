using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;

[System.Serializable]
public class NodeNarration
{
    public string nodeId;
    [TextArea(2, 5)]
    public string narrationText;
}

public class NarrationBubbleController : MonoBehaviour
{
    [Header("Sources")]
    [SerializeField] private GuideUIController guideUIController;
    [SerializeField] private VoiceQAController voiceQAController;
    [SerializeField] private RouteHighlighterController routeHighlighterController;

    [Header("Bubble UI")]
    [SerializeField] private Text speakerLabelText;
    [SerializeField] private Text bubbleText;
    [SerializeField] private Text transcriptText;

    [Header("Playback")]
    [SerializeField] private AudioSource narratorAudioSource;
    [SerializeField] private AudioClip placeholderNarrationClip;
    [SerializeField] private float charsPerSecond = 16f;

    [Header("Node Narration")]
    [SerializeField] private string apiBaseUrl = "http://127.0.0.1:8000";
    [SerializeField] private bool autoFetchFromBackend = true;
    [SerializeField] private bool useAIGCSpotNarration = true;
    [SerializeField] private string narrationUserProfile = "visitor";
    [SerializeField] private string narrationStyle = "friendly";
    [SerializeField] private string narrationLanguage = "zh";
    [SerializeField] private NodeNarration[] nodeNarrations;
    [SerializeField] private bool autoNarrateOnNodeArrival = true;

    private Coroutine typewriterCoroutine;
    private Coroutine spotNarrationCoroutine;
    private readonly Dictionary<string, string> nodeNarrationMap = new Dictionary<string, string>();

    private void Awake()
    {
        BuildNodeNarrationFromInspector();
    }

    private void OnEnable()
    {
        if (guideUIController != null)
        {
            guideUIController.GuideScriptReady += OnGuideScriptReady;
        }
        if (voiceQAController != null)
        {
            voiceQAController.VoiceAnswerReady += OnVoiceAnswerReady;
        }
        if (routeHighlighterController != null)
        {
            routeHighlighterController.NodeArrived += OnNodeArrived;
        }

        if (autoFetchFromBackend)
        {
            StartCoroutine(FetchSpotNarrations());
        }
    }

    private void OnDisable()
    {
        if (guideUIController != null)
        {
            guideUIController.GuideScriptReady -= OnGuideScriptReady;
        }
        if (voiceQAController != null)
        {
            voiceQAController.VoiceAnswerReady -= OnVoiceAnswerReady;
        }
        if (routeHighlighterController != null)
        {
            routeHighlighterController.NodeArrived -= OnNodeArrived;
        }
    }

    private void OnGuideScriptReady(string script)
    {
        PlayNarration("AI导览员", script, null);
    }

    private void OnVoiceAnswerReady(string transcript, string answer)
    {
        PlayNarration("语音问答助手", answer, "你问: " + transcript);
    }

    private void OnNodeArrived(string nodeId)
    {
        if (!autoNarrateOnNodeArrival)
        {
            return;
        }

        if (useAIGCSpotNarration)
        {
            if (spotNarrationCoroutine != null)
            {
                StopCoroutine(spotNarrationCoroutine);
            }
            spotNarrationCoroutine = StartCoroutine(FetchAndPlaySpotNarration(nodeId));
            return;
        }

        if (!nodeNarrationMap.TryGetValue(nodeId, out string text))
        {
            return;
        }

        PlayNarration("景点讲解", text, "当前节点: " + nodeId);
    }

    private void PlayNarration(string speaker, string content, string transcript)
    {
        if (speakerLabelText != null)
        {
            speakerLabelText.text = speaker;
        }

        if (transcriptText != null)
        {
            transcriptText.text = transcript ?? "";
        }

        if (typewriterCoroutine != null)
        {
            StopCoroutine(typewriterCoroutine);
        }
        typewriterCoroutine = StartCoroutine(Typewriter(content));

        if (narratorAudioSource != null && placeholderNarrationClip != null)
        {
            narratorAudioSource.Stop();
            narratorAudioSource.clip = placeholderNarrationClip;
            narratorAudioSource.Play();
        }
    }

    private IEnumerator Typewriter(string text)
    {
        if (bubbleText == null)
        {
            yield break;
        }

        bubbleText.text = "";
        string safeText = text ?? "";
        float delay = 1f / Mathf.Max(1f, charsPerSecond);

        for (int i = 0; i < safeText.Length; i++)
        {
            bubbleText.text += safeText[i];
            yield return new WaitForSeconds(delay);
        }
    }

    private void BuildNodeNarrationFromInspector()
    {
        nodeNarrationMap.Clear();
        if (nodeNarrations == null)
        {
            return;
        }

        foreach (NodeNarration item in nodeNarrations)
        {
            if (item == null || string.IsNullOrWhiteSpace(item.nodeId) || string.IsNullOrWhiteSpace(item.narrationText))
            {
                continue;
            }
            nodeNarrationMap[item.nodeId] = item.narrationText;
        }
    }

    private IEnumerator FetchSpotNarrations()
    {
        string url = apiBaseUrl + "/api/v1/spots";
        using (UnityWebRequest req = UnityWebRequest.Get(url))
        {
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                yield break;
            }

            SpotListResponse payload = JsonUtility.FromJson<SpotListResponse>(req.downloadHandler.text);
            if (payload == null || payload.spots == null)
            {
                yield break;
            }

            foreach (SpotInfo spot in payload.spots)
            {
                if (spot == null || string.IsNullOrWhiteSpace(spot.node_id) || string.IsNullOrWhiteSpace(spot.intro))
                {
                    continue;
                }
                nodeNarrationMap[spot.node_id] = spot.intro;
            }
        }
    }

    private IEnumerator FetchAndPlaySpotNarration(string nodeId)
    {
        SpotGuideRequest request = new SpotGuideRequest
        {
            node_id = nodeId,
            user_profile = narrationUserProfile,
            style = narrationStyle,
            language = narrationLanguage,
        };

        string url = apiBaseUrl + "/api/v1/guide/spot-generate";
        string json = JsonUtility.ToJson(request);
        byte[] payload = System.Text.Encoding.UTF8.GetBytes(json);

        using (UnityWebRequest req = new UnityWebRequest(url, "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(payload);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");

            yield return req.SendWebRequest();

            if (req.result == UnityWebRequest.Result.Success)
            {
                SpotGuideResponse resp = JsonUtility.FromJson<SpotGuideResponse>(req.downloadHandler.text);
                if (resp != null && !string.IsNullOrWhiteSpace(resp.script))
                {
                    PlayNarration(resp.title, resp.script, "当前节点: " + nodeId);
                    yield break;
                }
            }
        }

        if (nodeNarrationMap.TryGetValue(nodeId, out string fallbackText))
        {
            PlayNarration("景点讲解", fallbackText, "当前节点: " + nodeId);
        }
    }
}
