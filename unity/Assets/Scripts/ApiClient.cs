using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class ApiClient : MonoBehaviour
{
    [SerializeField] private string apiBaseUrl = "http://127.0.0.1:8000";

    public void PostJson<TReq, TResp>(string path, TReq body, Action<TResp> onSuccess, Action<string> onError)
    {
        StartCoroutine(PostJsonCoroutine(path, body, onSuccess, onError));
    }

    private IEnumerator PostJsonCoroutine<TReq, TResp>(string path, TReq body, Action<TResp> onSuccess, Action<string> onError)
    {
        string url = apiBaseUrl + path;
        string json = JsonUtility.ToJson(body);
        byte[] payload = System.Text.Encoding.UTF8.GetBytes(json);

        using (UnityWebRequest req = new UnityWebRequest(url, "POST"))
        {
            req.uploadHandler = new UploadHandlerRaw(payload);
            req.downloadHandler = new DownloadHandlerBuffer();
            req.SetRequestHeader("Content-Type", "application/json");
            yield return req.SendWebRequest();

            if (req.result != UnityWebRequest.Result.Success)
            {
                onError?.Invoke(req.error + " | " + req.downloadHandler.text);
                yield break;
            }

            try
            {
                TResp data = JsonUtility.FromJson<TResp>(req.downloadHandler.text);
                onSuccess?.Invoke(data);
            }
            catch (Exception e)
            {
                onError?.Invoke("JSON parse error: " + e.Message + " | raw: " + req.downloadHandler.text);
            }
        }
    }
}
