using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GuideUIController : MonoBehaviour
{
    public event Action<List<string>> RoutePlanned;
    public event Action<string> GuideScriptReady;

    [Header("Network")]
    [SerializeField] private ApiClient apiClient;

    [Header("Inputs")]
    [SerializeField] private InputField startIdInput;
    [SerializeField] private InputField endIdInput;
    [SerializeField] private Dropdown profileDropdown;
    [SerializeField] private Dropdown styleDropdown;

    [Header("Buttons")]
    [SerializeField] private Button planButton;
    [SerializeField] private Button guideButton;

    [Header("Output")]
    [SerializeField] private Text resultText;

    private List<string> currentRoute = new List<string>();

    private readonly string[] profiles = { "new_student", "parent", "visitor", "alumni" };
    private readonly string[] styles = { "formal", "friendly", "storytelling" };

    private void Awake()
    {
        if (planButton != null)
        {
            planButton.onClick.AddListener(OnPlanClicked);
        }
        if (guideButton != null)
        {
            guideButton.onClick.AddListener(OnGuideClicked);
        }
    }

    private void OnPlanClicked()
    {
        RoutePlanRequest req = new RoutePlanRequest
        {
            start_id = startIdInput.text.Trim(),
            end_id = endIdInput.text.Trim(),
            avoid_crowded = true,
            prefer_indoor = false
        };

        apiClient.PostJson<RoutePlanRequest, RoutePlanResponse>(
            "/api/v1/route/plan",
            req,
            onSuccess: (resp) =>
            {
                currentRoute = resp.node_path ?? new List<string>();
                resultText.text = "路线规划成功\n"
                    + "总距离: " + resp.total_distance + " m\n"
                    + "预计时间: " + resp.estimated_minutes + " min\n"
                    + "路径: " + string.Join(" -> ", currentRoute);
                RoutePlanned?.Invoke(new List<string>(currentRoute));
            },
            onError: (err) =>
            {
                resultText.text = "路线规划失败: " + err;
            }
        );
    }

    private void OnGuideClicked()
    {
        if (currentRoute == null || currentRoute.Count < 2)
        {
            resultText.text = "请先规划路线。";
            return;
        }

        GuideGenerateRequest req = new GuideGenerateRequest
        {
            user_profile = profiles[Mathf.Clamp(profileDropdown.value, 0, profiles.Length - 1)],
            style = styles[Mathf.Clamp(styleDropdown.value, 0, styles.Length - 1)],
            language = "zh",
            route_nodes = currentRoute
        };

        apiClient.PostJson<GuideGenerateRequest, GuideGenerateResponse>(
            "/api/v1/guide/generate",
            req,
            onSuccess: (resp) =>
            {
                resultText.text = resp.title + "\n\n" + resp.script;
                GuideScriptReady?.Invoke(resp.script);
            },
            onError: (err) =>
            {
                resultText.text = "讲解生成失败: " + err;
            }
        );
    }
}
