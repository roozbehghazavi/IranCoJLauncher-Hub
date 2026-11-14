EmiterDef()
{
	Space("world")

	LifeTime()
	{
		keyf(0, 1.2)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 8)
	}

	StartVelocity()
	{
		keyf(0, 1000)
	}

	StartVelocityRand()
	{
		keyv(0, 150, 300, 300)
	}

	Direction()
	{
		keyv(0, -1, 0, 0)
	}

	GenArea("point")
}
