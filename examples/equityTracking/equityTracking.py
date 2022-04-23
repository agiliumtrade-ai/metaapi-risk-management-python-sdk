from metaapi_cloud_sdk import RiskManagement, DrawdownListener
import os
import asyncio
import json

# your MetaApi API token
token = os.getenv('TOKEN') or '<put in your token here>'
# your MetaApi account id
# the account must have field riskManagementApiEnabled set to true
account_id = os.getenv('ACCOUNT_ID') or '<put in your account id here>'
domain = os.getenv('DOMAIN')


async def main():
    risk_management = RiskManagement(token, {'domain': domain})
    risk_management_api = risk_management.risk_management_api

    class ExampleDrawdownListener(DrawdownListener):
        async def on_drawdown(self, drawdown_event):
            print('drawdown event received', drawdown_event)

    try:
        # creating a tracker
        tracker_id = await risk_management_api.create_drawdown_tracker(account_id, {
            'name': 'example-tracker',
            'absoluteDrawdownThreshold': 5,
            'period': 'day'
        })
        print('Created a drawdown tracker ' + tracker_id['id'])

        # adding a drawdown listener
        drawdown_listener = ExampleDrawdownListener()
        listener_id = risk_management_api.add_drawdown_listener(drawdown_listener, account_id, tracker_id['id'])

        print('Streaming drawdown events for 1 minute...')
        await asyncio.sleep(60)
        risk_management_api.remove_drawdown_listener(listener_id)

        print('Receiving statistics with REST API')
        events = await risk_management_api.get_drawdown_events(None, None, account_id, tracker_id['id'])
        print('drawdown events', json.dumps(events))
        statistics = await risk_management_api.get_drawdown_statistics(account_id, tracker_id['id'])
        print('drawdown statistics', json.dumps(statistics))
        equity_chart = await risk_management_api.get_equity_chart(account_id)
        print('equity chart', json.dumps(equity_chart))

        # removing the tracker
        await risk_management_api.delete_drawdown_tracker(account_id, tracker_id['id'])
        print('Removed the tracker')
    except Exception as err:
        print(risk_management.format_error(err))
    exit()

asyncio.run(main())
