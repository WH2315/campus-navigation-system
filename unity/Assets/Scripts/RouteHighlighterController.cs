using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class NodeAnchor
{
    public string nodeId;
    public Transform anchor;
}

public class RouteHighlighterController : MonoBehaviour
{
    public event Action<string> NodeArrived;

    [Header("Source")]
    [SerializeField] private GuideUIController guideUIController;

    [Header("Route Visual")]
    [SerializeField] private LineRenderer routeLine;
    [SerializeField] private NodeAnchor[] nodeAnchors;

    [Header("Route Marker")]
    [SerializeField] private Transform marker;
    [SerializeField] private float markerSpeed = 3f;

    private readonly Dictionary<string, Transform> anchorMap = new Dictionary<string, Transform>();
    private Coroutine markerCoroutine;

    private void Awake()
    {
        anchorMap.Clear();
        if (nodeAnchors == null)
        {
            return;
        }

        foreach (NodeAnchor item in nodeAnchors)
        {
            if (item == null || string.IsNullOrWhiteSpace(item.nodeId) || item.anchor == null)
            {
                continue;
            }
            anchorMap[item.nodeId] = item.anchor;
        }
    }

    private void OnEnable()
    {
        if (guideUIController != null)
        {
            guideUIController.RoutePlanned += OnRoutePlanned;
        }
    }

    private void OnDisable()
    {
        if (guideUIController != null)
        {
            guideUIController.RoutePlanned -= OnRoutePlanned;
        }
    }

    private void OnRoutePlanned(List<string> routeNodeIds)
    {
        if (routeLine == null)
        {
            return;
        }

        List<Vector3> points = new List<Vector3>();
        foreach (string nodeId in routeNodeIds)
        {
            if (!anchorMap.TryGetValue(nodeId, out Transform anchor))
            {
                continue;
            }
            points.Add(anchor.position);
        }

        routeLine.positionCount = points.Count;
        for (int i = 0; i < points.Count; i++)
        {
            routeLine.SetPosition(i, points[i]);
        }

        if (points.Count == 0 || marker == null)
        {
            return;
        }

        marker.position = points[0];
        if (routeNodeIds.Count > 0)
        {
            NodeArrived?.Invoke(routeNodeIds[0]);
        }
        if (markerCoroutine != null)
        {
            StopCoroutine(markerCoroutine);
        }
        markerCoroutine = StartCoroutine(MoveMarker(points, routeNodeIds));
    }

    private IEnumerator MoveMarker(List<Vector3> points, List<string> routeNodeIds)
    {
        for (int i = 1; i < points.Count; i++)
        {
            Vector3 target = points[i];
            while (Vector3.Distance(marker.position, target) > 0.05f)
            {
                marker.position = Vector3.MoveTowards(marker.position, target, markerSpeed * Time.deltaTime);
                yield return null;
            }
            marker.position = target;
            if (i < routeNodeIds.Count)
            {
                NodeArrived?.Invoke(routeNodeIds[i]);
            }
            yield return new WaitForSeconds(0.1f);
        }
    }
}
