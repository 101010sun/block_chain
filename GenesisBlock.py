from Format import Block
from Format import BlockChain

def create_genesis_block(self):
    print("Create genesis block...")
    new_block = Block('https://www.youtube.com/watch?v=QuUWPqlhuNU&ab_channel=%E5%8B%95%E7%89%A9%E5%AE%B6','IM53Q101010SUNALLEN0201')
    new_block.hash = self.get_hash(new_block,0)
    self.chain.append(new_block) #Add genesis to blockchain