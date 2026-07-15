from flask import Blueprint, jsonify, Response
from utils.aws_client import get_aws_client
import datetime

cost_bp = Blueprint('cost', __name__)

def get_real_cost_data():
    ce = get_aws_client('ce')
    if not ce:
        return None, 0, "Failed to connect to AWS Cost Explorer"

    now = datetime.datetime.utcnow()
    # AWS CE requires end date to be exclusive and strictly after start date
    start = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    
    # If it's the exact same day (e.g., ran exactly at midnight edge case), offset by 1 day
    if start == end:
        start = (now - datetime.timedelta(days=31)).strftime('%Y-%m-%d')

    try:
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        service_totals = {}
        total_cost = 0.0
        
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service_name = group['Keys'][0]
                amount = float(group['Metrics']['UnblendedCost']['Amount'])
                service_totals[service_name] = service_totals.get(service_name, 0.0) + amount
                total_cost += amount
                
        services_cost = []
        for srv, amt in service_totals.items():
            if amt > 0:
                services_cost.append({'service': srv, 'amount': amt})
                
        services_cost.sort(key=lambda x: x['amount'], reverse=True)
        return services_cost, total_cost, None
        
    except Exception as e:
        return None, 0, str(e)


@cost_bp.route('/summary', methods=['GET'])
def get_cost_summary():
    services_cost, total_cost, error = get_real_cost_data()
    
    if error:
        # Fallback empty state if Cost Explorer is not enabled on account
        return jsonify({
            'total_estimated_cost': 0.00,
            'currency': 'USD',
            'budget_limit': 50.00,
            'services': [{'service': f'Error: {error}', 'amount': 0.0}],
            'error': error
        })
    
    return jsonify({
        'total_estimated_cost': round(total_cost, 2),
        'currency': 'USD',
        'budget_limit': 50.00,
        'services': services_cost
    })

@cost_bp.route('/download_invoice', methods=['GET'])
def download_invoice():
    services_cost, total_cost, error = get_real_cost_data()
    
    csv_data = "Service Name,Amount (USD)\n"
    if error:
        csv_data += f'"Error fetching cost data: {error}",$0.00\n'
    else:
        for item in services_cost:
            csv_data += f'"{item["service"]}",${item["amount"]:.2f}\n'
        csv_data += f"\nTotal Estimated Cost,${total_cost:.2f}\n"
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=aws_cost_invoice.csv"}
    )
