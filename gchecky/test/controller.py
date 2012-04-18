import unittest

import gchecky.controller as gcontroller

class ControllerTestCase(unittest.TestCase):
    def setUp(self):
        GCHECKOUT_VENDOR_ID = '552688368931861'
        GCHECKOUT_MERCHANT_KEY = 'fse2vefEHSu8lQ2g-o6kZQ'
        self.controller = gcontroller.Controller(GCHECKOUT_VENDOR_ID,
                                                 GCHECKOUT_MERCHANT_KEY,
                                                 True)
    def testArchiving(self):
        self.controller.unarchive_order('457164429557231')
        self.controller.archive_order('457164429557231')
    def testMessaging(self):
        self.controller.send_buyer_message('457164429557231', 'Test message.')
    def testMerchantOrderNumber(self):
        self.controller.add_merchant_order_number('457164429557231', 'BLA123456-BLA')
    def testTrackingData(self):
        self.controller.add_tracking_data('457164429557231',
                                          'UPS',
                                          'ARGHHH-UPS-NUMBER123456')
    def testChargeOrder(self):
        self.controller.charge_order('920492774454564', 1599)
    def testRefundOrder(self):
        self.controller.refund_order('457164429557231', 0.04,
                                     'Test refunding mechanism', 'Oh la la!')
    def testAuthorizeOrder(self):
        self.controller.authorize_order('457164429557231')
    def testCancelOrder(self):
        self.controller.cancel_order('566018579274459',
                                     'Test order cancelling', 'Oh al al!')
    def testProcessOrder(self):
        self.controller.process_order('920492774454564')
    def testDeliverOrder(self):
        self.controller.deliver_order('920492774454564', send_email=True)

def controllerSuite():
    suite = unittest.TestSuite()
#    suite.addTest(ControllerTestCase('testArchiving'))
#    suite.addTest(ControllerTestCase('testMessaging'))
#    suite.addTest(ControllerTestCase('testMerchantOrderNumber'))
#    suite.addTest(ControllerTestCase('testTrackingData'))

    suite.addTest(ControllerTestCase('testChargeOrder'))
#    suite.addTest(ControllerTestCase('testRefundOrder'))

#    suite.addTest(ControllerTestCase('testAuthorizeOrder'))
#    suite.addTest(ControllerTestCase('testCancelOrder'))
    suite.addTest(ControllerTestCase('testProcessOrder'))
    suite.addTest(ControllerTestCase('testDeliverOrder'))
    return suite

if __name__ == '__main__':
    unittest.main()


