# CloudWatch Log Group for Nginx Access logs
resource "aws_cloudwatch_log_group" "nginx_access" {
  name              = "/aws/ec2/${var.project_name}/nginx-access"
  retention_in_days = 7 # Keep logs for 7 days (cost control)
}

# CloudWatch Log Group for Nginx Error logs
resource "aws_cloudwatch_log_group" "nginx_error" {
  name              = "/aws/ec2/${var.project_name}/nginx-error"
  retention_in_days = 7
}

# SNS Topic for Alarms (created only if alert_email is provided)
resource "aws_sns_topic" "alerts" {
  count = var.alert_email != "" ? 1 : 0
  name  = "${var.project_name}-alerts"
}

# Email subscription for SNS Topic
resource "aws_sns_topic_subscription" "email_sub" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# Metric Filter to detect errors (e.g. 500 status codes) in Nginx Access logs
resource "aws_cloudwatch_log_metric_filter" "nginx_500_errors" {
  name           = "Nginx500ErrorCount"
  pattern        = "\"HTTP/1.1 500\"" # Matches HTTP 500 errors in Nginx access log format
  log_group_name = aws_cloudwatch_log_group.nginx_access.name

  metric_transformation {
    name      = "Nginx500Errors"
    namespace = "WebServerMetrics"
    value     = "1"
  }
}

# CloudWatch Alarm for Nginx 500 Errors
resource "aws_cloudwatch_metric_alarm" "nginx_500_alarm" {
  count               = var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-nginx-500-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = aws_cloudwatch_log_metric_filter.nginx_500_errors.metric_transformation[0].name
  namespace           = aws_cloudwatch_log_metric_filter.nginx_500_errors.metric_transformation[0].namespace
  period              = 60 # 1 minute
  statistic           = "Sum"
  threshold           = 5 # Alarm if there are 5 or more 500 errors in a minute
  alarm_description   = "Triggered when Nginx access logs detect 5 or more HTTP 500 status codes in 1 minute."
  alarm_actions       = [aws_sns_topic.alerts[0].arn]
}

# CloudWatch Alarm for VM Status Checks (Uptime check at instance level)
resource "aws_cloudwatch_metric_alarm" "instance_status_check_alarm" {
  count               = var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0 # Alarm if status check fails (value > 0)
  alarm_description   = "Triggered when the EC2 instance status check fails (basic VM uptime check)."
  alarm_actions       = [aws_sns_topic.alerts[0].arn]

  dimensions = {
    InstanceId = aws_instance.ticket_api_instance.id
  }
}
