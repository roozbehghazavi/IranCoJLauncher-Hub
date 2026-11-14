EmiterDef()
{
	LifeTime()
	{
		keyf(0, 0.6)
	}

	GenType("one_time")

	NumParticles()
	{
		keyf(0, 5)
	}

	StartVelocity()
	{
		keyf(0, 300)
	}

	StartVelocityRand()
	{
		keyv(0, 200, 200, 200)
	}

	Direction()
	{
		keyv(0, 0, -1, 0)
	}

	GenArea("point")
}
