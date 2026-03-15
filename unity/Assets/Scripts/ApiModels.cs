using System;
using System.Collections.Generic;

[Serializable]
public class RoutePlanRequest
{
    public string start_id;
    public string end_id;
    public bool avoid_crowded;
    public bool prefer_indoor;
}

[Serializable]
public class RouteSegment
{
    public string from_id;
    public string to_id;
    public float distance;
}

[Serializable]
public class RoutePlanResponse
{
    public List<string> node_path;
    public float total_distance;
    public int estimated_minutes;
    public List<RouteSegment> segments;
}

[Serializable]
public class GuideGenerateRequest
{
    public string user_profile;
    public string style;
    public string language;
    public List<string> route_nodes;
}

[Serializable]
public class GuideGenerateResponse
{
    public string title;
    public string script;
}

[Serializable]
public class ASRResponse
{
    public string text;
}

[Serializable]
public class VoiceChatResponse
{
    public string transcript;
    public string answer;
}

[Serializable]
public class SpotInfo
{
    public string node_id;
    public string name;
    public string category;
    public string intro;
}

[Serializable]
public class SpotListResponse
{
    public List<SpotInfo> spots;
}

[Serializable]
public class SpotGuideRequest
{
    public string node_id;
    public string user_profile;
    public string style;
    public string language;
}

[Serializable]
public class SpotGuideResponse
{
    public string title;
    public string script;
}
